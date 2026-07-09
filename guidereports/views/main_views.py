from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from ..models import *
from django.forms import inlineformset_factory
from ..forms import *

import reportlab
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

import datetime
from django.shortcuts import redirect

from datetime import datetime
from django.http import FileResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import urllib.request 
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


@login_required
def index(request): 
    guidereports = GuideReport.objects.all().order_by('-id')
    return render(request, 'guidereports/index.html', {'guidereports': guidereports})

@login_required
def DetailView(request, pk):
    guide_report = get_object_or_404(GuideReport, pk=pk)
    events = guide_report.events.all()
    event_fee = guide_report.final_events_fee
    expense_fee = guide_report.final_expenses_fee
    fuel_fee = guide_report.final_fuels_fee
    final_amount_due = guide_report.final_amount_due
    super_ann = guide_report.super_ann
    invoice_number = guide_report.invoice_number

    return render(request, 'guidereports/detail.html', {
        'guide_report': guide_report,
        'events': events,
        'event_fee': event_fee, 
        'expense_fee': expense_fee, 
        'fuel_fee': fuel_fee,
        'final_amount_due': final_amount_due, 
        'super_ann': super_ann,         
        'invoice_number': invoice_number       
    })

@login_required
def delete_guidereport(request, pk):
    guidereport = get_object_or_404(GuideReport, pk=pk)

    if request.method == "POST": 
        guidereport.delete()
        return redirect('mypage:index')
    
    return render(request, 'guidereports/guidereport_confirm_delete.html', {'guidereport': guidereport})


@login_required
def guidereport_confirm(request, pk): 
    if request.method == 'POST': 
        guide_report = get_object_or_404(GuideReport, id=pk)
        guide_report.is_confirmed = not guide_report.is_confirmed
        guide_report.save()

    return redirect('guidereports:detail', pk=pk)


@login_required
def guidereport_pay(request, pk): 
    if request.method == 'POST': 
        guide_report = get_object_or_404(GuideReport, id=pk)
        guide_report.is_paid = not guide_report.is_paid
        guide_report.save()

    return redirect('guidereports:detail', pk=pk)
        

@login_required
def update_guidereport(request, pk): 
    guidereport = get_object_or_404(GuideReport, pk=pk)
    
    request.session['main_data'] = {
        'guidereport_id': guidereport.id, 
        'day_inbound': guidereport.day_inbound,
        'role': guidereport.role,
    }
    
    if guidereport.day_inbound == 'INBOUND': 
        request.session['inbound_data'] = {
            'guidereport_id': guidereport.id,
            'role': guidereport.role,
            'day_inbound': guidereport.day_inbound, 
            'agency_code': guidereport.agency_code,
            'adt': guidereport.adt,
            'tc': guidereport.tc, 
            'chd': guidereport.chd
        }
    return redirect('guidereports:guidereport_main')


@login_required
def guidereport_main(request): 
    if request.method == 'POST': 
        form = GuideReportMainForm(request.POST)
        if form.is_valid(): 
            existing_data = request.session.get('main_data', {})
            day_inbound = form.cleaned_data['day_inbound']
            existing_data['day_inbound'] = day_inbound
            existing_data['role'] = form.cleaned_data['role']
            
            request.session['main_data'] = existing_data
            
            if day_inbound == 'DAY': 
                return redirect('guidereports:guidereport_day')
            elif day_inbound == 'INBOUND': 
                return redirect('guidereports:guidereport_inbound_agency') 
    else: 
        if request.GET.get('new') == '1':
            request.session.pop('main_data', None)
            request.session.pop('inbound_data', None) 

        saved_main_data = request.session.get('main_data')

        if saved_main_data:
            form = GuideReportMainForm(initial=saved_main_data)
        else:
            form = GuideReportMainForm()
    
    return render(request, 'guidereports/guidereport_main.html', {
        'form': form, 
        'INBOUND_ROLE': INBOUND_ROLE,
        'DAY_ROLE': DAY_ROLE
    })

@login_required
def guidereport_pdf(request, pk):
    font_name = "NanumGothic"
    font_url = "https://fonts.gstatic.com/s/nanumgothic/v23/PN_oRfi-QnsS4F7NQ_7927GEL6V2Kg.ttf"
    font_path = os.path.join("/tmp", "NanumGothic.ttf") if os.name != 'nt' else os.path.join(os.environ.get('TEMP', ''), 'NanumGothic.ttf')

    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_url, font_path)
        except Exception:
            pass

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        font_name = "Helvetica"

    guide_report = get_object_or_404(GuideReport, id=pk)
    events = guide_report.events.all()
    
    invoice_number = f"INV-{int(guide_report.invoice_number):04d}"
    
    event_subtotal = 0
    event_list_data = []
    for event in events:
        g_fee = float(event.guide_fee or 0)
        event_subtotal += g_fee
        date_str = event.report_date if event.report_date else ""
        
        hours_str = f" ({event.hours})" if guide_report.day_inbound == 'INBOUND' and event.hours else ""
        event_list_data.append((f"{date_str} |  {event.eventcode}{hours_str}", f"${g_fee:,.2f}"))
    
    expense_subtotal = 0
    expense_list_data = []

    for exp in guide_report.expenses.all():
        e_fee = float(exp.expense or 0)
        expense_subtotal += e_fee
        expense_list_data.append((f"", f"{exp.expense_type}", f"${e_fee:,.2f}"))
    
    for event in guide_report.events.all():
        if event.overtime and int(event.overtime) > 0:
            ov_time = int(event.overtime)
            ov_fee = ov_time * 30
            expense_subtotal += ov_fee
            expense_list_data.append((f"{event.report_date}", f"Overtime {ov_time} hrs", f"${ov_fee:,.2f}"))

    final_amount_due = event_subtotal + expense_subtotal
    super_ann = final_amount_due * 0.115 

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    invoice_style = ParagraphStyle(
        'InvoiceTitle', parent=styles['Heading1'], fontName=font_name,
        fontSize=22, leading=26, textColor=colors.HexColor('#2d3436'), spaceAfter=6
    )
    invoice_number_style = ParagraphStyle(
        'InvoiceNumber', parent=styles['Heading3'], fontName=font_name,
        fontSize=10,  textColor=colors.HexColor('#2d3436')
    )
    date_tag_style = ParagraphStyle(
        'InvoiceDate', parent=styles['Normal'], fontName=font_name,
        fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15
    )
    th_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], fontName=font_name,
        fontSize=11, textColor=colors.HexColor('#ffffff')
    )
    td_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName=font_name,
        fontSize=10, textColor=colors.HexColor('#2d3436'), leading=14
    )
    td_bold_style = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'], fontName=font_name,
        fontSize=10, textColor=colors.HexColor('#2d3436'), leading=14
    )
    section_title_style = ParagraphStyle(
        'SectionTitle', parent=styles['Heading2'], fontName=font_name,
        fontSize=14, leading=18, textColor=colors.HexColor('#2d3436'), spaceBefore=15, spaceAfter=8
    )
    total_style_label = ParagraphStyle(
        'TotalLabel', parent=styles['Normal'], fontName=font_name, 
        fontSize=11, leading=14, textColor=colors.HexColor('#64748b'),
        alignment=0 
    )
    total_style_val = ParagraphStyle(
        'TotalVal', parent=styles['Normal'], fontName=font_name, 
        fontSize=20, leading=24, textColor=colors.HexColor('#2d3436'),
        alignment=0 
    )

    story = []

    inv_date_str = guide_report.invoice_date.strftime("%d-%b-%Y") if guide_report.invoice_date else ""
    story.append(Paragraph("INVOICE", invoice_style))
    story.append(Paragraph(f"#{invoice_number}", invoice_number_style))
    story.append(Paragraph(f"REF {guide_report.group_code or ''}", invoice_number_style))
    story.append(Paragraph(f"<b>Invoice Date:</b> {inv_date_str}", date_tag_style))

    guide_name = guide_report.guide.name if hasattr(guide_report.guide, 'name') else request.user.first_name
    payment_details = f"""
    <b>Guide</b><br/>
    <font color="#2d3436" size="11"><b>{guide_name}</b></font><br/>
    ABN: {getattr(guide_report.guide, 'abn', '')}<br/>
    Contact: {getattr(guide_report.guide, 'contact_info', '')}<br/>
    <font color="#64748b">Australia</font><br/>
    """

    bsb = getattr(guide_report.guide, 'bsb', '')
    account_number = getattr(guide_report.guide, 'account_number', '')
    
    admin = Guide.objects.get(contact_info='account@joystudytour.com.au')
    print("admin: ", admin.abn)

    bill_to = f"""
    <b>Bill To</b><br/>
    <font color="#2d3436" size="11"><b>Joy Study & Tour Pty Ltd</b></font><br/>
    ABN: {admin.abn}<br/>
    Contact: {admin.contact_info}<br/>
    <font color="#64748b">Australia</font><br/>
    """
    
    info_table_data = [
        [Paragraph(payment_details, td_style), Paragraph(bill_to, td_style)]
    ]
    info_table = Table(info_table_data, colWidths=[300, 215])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINELEFT', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINERIGHT', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    pax_str = "-"
    if guide_report.day_inbound == 'INBOUND':
        adt_val = guide_report.adt if guide_report.adt is not None else 0
        chd_val = guide_report.chd if guide_report.chd is not None else 0
        tc_val = guide_report.tc if guide_report.tc is not None else 0
        pax_str = f"ADT: {adt_val}   CHD: {chd_val}   TC: {tc_val}"

    pax_section_style = ParagraphStyle(
        'PaxSection',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        textColor=colors.HexColor('#2d3436'),
        leading=16,
        backColor=colors.HexColor('#edf2f7'),  
        borderColor=colors.HexColor('#cbd5e0'), 
        borderWidth=0.5,
        borderPadding=5,                     
        spaceAfter=10                         
    )
    
    day_inbound_val = guide_report.day_inbound or ''
    role_val = guide_report.role or ''

    pax_text = f"""
    <b>DAY/INBOUND:</b> {day_inbound_val} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Role:</b> {role_val}
    """

    story.append(Paragraph(pax_text, pax_section_style))    
    story.append(Spacer(1, 10))

    story.append(Paragraph("Events", section_title_style))
    event_table_rows = [[Paragraph("<b>Description</b>", th_style), Paragraph("<b>Amount</b>", th_style)]]
    
    for desc, amt in event_list_data:
        event_table_rows.append([Paragraph(desc, td_style), Paragraph(amt, td_style)])
    
    event_table_rows.append([Paragraph("<b>Event Subtotal (inc. GST)</b>", td_bold_style), Paragraph(f"<b>${event_subtotal:,.2f}</b>", td_bold_style)])
    
    event_table = Table(event_table_rows, colWidths=[400, 115])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#2d3436')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'), 
        ('BACKGROUND', (0,-1), (1,-1), colors.HexColor('#f8f9fa')), 
    ]))
    story.append(event_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("Guide Expenses", section_title_style))
    exp_table_rows = [[Paragraph("<b>Expense Type</b>", th_style), Paragraph("<b>Amount</b>", th_style)]]
    if expense_list_data:
        for report_date, desc, amt in expense_list_data:
            if report_date:
                exp_table_rows.append([Paragraph(f"{report_date} | {desc}", td_style), Paragraph(amt, td_style)])
            else: 
                exp_table_rows.append([Paragraph(desc, td_style), Paragraph(amt, td_style)])
    else:
        exp_table_rows.append([Paragraph("등록된 비용이 없습니다.", td_style), Paragraph("$0.00", td_style)])
        
    exp_table_rows.append([Paragraph("<b>Expense Subtotal (inc. GST)</b>", td_bold_style), Paragraph(f"<b>${expense_subtotal:,.2f}</b>", td_bold_style)])
    
    exp_table = Table(exp_table_rows, colWidths=[400, 115])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#2d3436')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BACKGROUND', (0,-1), (1,-1), colors.HexColor('#f8f9fa')),
    ]))
    story.append(exp_table)
    story.append(Spacer(1, 25))

    total_style_label = ParagraphStyle('TotalLabel', parent=styles['Normal'], fontName=font_name, fontSize=11, textColor=colors.HexColor('#64748b'))
    total_style_val = ParagraphStyle('TotalVal', parent=styles['Normal'], fontName=font_name, fontSize=20, textColor=colors.HexColor('#2d3436'))
    
    total_table_data = [
        [Paragraph("<b>TOTAL (INC. GST)</b>", total_style_label)]
    ]
    if request.user.username == 'admin':
        total_table_data = [
            [Paragraph("<b>TOTAL (INC. GST)</b>", total_style_label), Paragraph("<b>SUPERANNUATION</b>", total_style_label)],
            [Paragraph(f"<b>${final_amount_due:,.2f}</b>", total_style_val), Paragraph(f"<b>${super_ann:,.2f}</b>", total_style_val)]
        ]
        total_widths = [257.5, 257.5]
    else:
        total_table_data = [
            [Paragraph("<b>TOTAL (INC. GST)</b>", total_style_label)],
            [Paragraph(f"<b>${final_amount_due:,.2f}</b>", total_style_val)]
        ]
        total_widths = [515]

    total_table = Table(total_table_data, colWidths=total_widths)
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#edf2f7')),
        ('PADDING', (0,0), (-1,-1), 12),      
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))

    story.append(KeepTogether([total_table]))
    story.append(Spacer(1, 20))

    bank_account_name = guide_report.guide.bank_account_name

    bsb_account_table_data = [
        [Paragraph("<b>Bank Account Name</b>", td_bold_style), Paragraph(bank_account_name, td_style)],
        [Paragraph("<b>BSB</b>", td_bold_style), Paragraph(bsb, td_style)],
        [Paragraph("<b>Account Number</b>", td_bold_style), Paragraph(account_number, td_style)],
    ]
    bsb_account_table = Table(bsb_account_table_data, colWidths=[150, 365])
    bsb_account_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINELEFT', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('LINERIGHT', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(bsb_account_table)
    story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)

    clean_group_code = (guide_report.group_code or '').strip().replace(' ', '_')
    pdf_filename = f"{invoice_number}_{clean_group_code}.pdf"
    
    return FileResponse(buffer, as_attachment=False, content_type='application/pdf', filename=pdf_filename)