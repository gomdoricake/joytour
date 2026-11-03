// JOY 6A 처럼 티켓 수배 결과에 #A 가 있는 경우 제목
// 필립 아일랜드에 대해서는 처리하지 않음. 

function fromSheetToCalendar() {
    const DAY_CALENDAR_ID =
    "c_0d796ef832d67710449d446a85ac9c550436adf027f8ffa0fa0d35df2ae5ae90@group.calendar.google.com";

    const DAY_SHEET_ID = "1ZM4YqH-g6YMzIy3gS7GW3bhDhpQOp3qYh2mRGEHXSGo";

    const dayCalendar = CalendarApp.getCalendarById(DAY_CALENDAR_ID);
    const daySheet = SpreadsheetApp.openById(DAY_SHEET_ID); 

    var today = new Date();
    today.setHours(0, 0, 0, 0); // 비교를 위해 오늘의 시작 시간(00:00:00)으로 맞춤

    const year = today.getFullYear() + 1; 

    var oneWeekLater = new Date(year, 11, 15);
    oneWeekLater.setHours(23, 59, 59, 999); // 그날의 끝 시간으로 맞춤

    // ZGOR, GOR
    const endOfYear = new Date(year, 11, 31); 
    endOfYear.setHours(23, 59, 59, 999);

    const sheet = daySheet.getSheetByName("예약 리스트");
    var rows = sheet.getDataRange().getValues(); 

    if (rows.length < 2) {
      Logger.log("데이터가 없거나 헤더만 존재합니다.");
      return; 
    }

    var headerRow = rows[0]; 
    var targetColumnIndex = headerRow.indexOf("캘린더 정상 여부"); 
    var pNameIdx = headerRow.indexOf('플랫폼 코드');
    var nameIdx  = headerRow.indexOf('이름');
    var adtIdx   = headerRow.indexOf('성인');
    var chdIdx   = headerRow.indexOf('아동');
    var infIdx   = headerRow.indexOf('영아');
    var phoneIdx = headerRow.indexOf('연락처');

    var travelDateIdxs = [headerRow.indexOf('여행일1'), headerRow.indexOf('여행일2'), headerRow.indexOf('여행일3')];
    var optionIdxs     = [headerRow.indexOf('옵션1'), headerRow.indexOf('옵션2'), headerRow.indexOf('옵션3')];

    if (targetColumnIndex == -1) {
      Logger.log(" '캘린더 정상 여부' 열을 찾을 수 없습니다.");
      return;
    }

    // 매핑용 딕셔너리 객체
    var itineraryCode = {
      '그레이트오션로드': 'GOR',
      '소규모 그레이트오션로드': 'ZGOR',
      '퍼핑+필립': 'PP',
      '퍼핑빌리': 'PB',
      '필립아일랜드': 'PI',
      '모닝턴': 'MON',
      '아침 모닝턴': 'AMON',
      '오후 모닝턴': 'PMON',
      '와이너리': 'YV',
      '시티': 'CT',
      '소버린 힐': 'SOV'
    };

    // 2번째 줄부터 데이터 읽기 시작

    for (var i = 1; i < rows.length; i++) {

      var currentRow = rows[i];
      var statusValue = currentRow[targetColumnIndex];

      // 이미 처리가 완료되었으면 건너뛰기
      if (statusValue === true || statusValue === "TRUE") continue;
      var platform = currentRow[pNameIdx];
      var name     = currentRow[nameIdx];
      var adt      = currentRow[adtIdx] ? currentRow[adtIdx] : '0';
      var chd      = currentRow[chdIdx] ? currentRow[chdIdx] : '0';
      var inf      = currentRow[infIdx] ? currentRow[infIdx] : '0';
      var phone    = currentRow[phoneIdx];

      // 3개의 여행일과 옵션을 배열로 세팅
      var dates = [currentRow[travelDateIdxs[0]], currentRow[travelDateIdxs[1]], currentRow[travelDateIdxs[2]]];
      var options = [currentRow[optionIdxs[0]], currentRow[optionIdxs[1]], currentRow[optionIdxs[2]]];

      for (var j = 0; j < 3; j++) {
        var date = dates[j];
        var option = options[j];
        var group_code = itineraryCode[option];


        // <테스트> GOR 또는 ZGOR 이 아닐 경우에 패스
        if (!(group_code == 'GOR' || group_code == 'ZGOR' || group_code == 'MON' || group_code == 'CT' || group_code == 'YV' || group_code == 'SOV')) {
          continue; 
        }

        // 날짜가 없거나 옵션 코드 매핑이 안 되는 경우 건너뛰기
        if (!date || !group_code) {
          continue;
        }

        var targetDate = new Date(date);

        if (isNaN(targetDate.getTime())) {
          Logger.log((i + 1) + "번째 줄의 " + (j + 1) + "번째 여행일: 올바른 날짜 형식이 아닙니다 -> " + date);
          continue;      
        }

        var tillWhen;

        if (group_code === "ZGOR" || group_code === "GOR") {
          tillWhen = endOfYear;
        } else {
          tillWhen = oneWeekLater;
        }

        // 날짜 필터링 검사 (오늘 이전이거나, 지정된 마감 범위를 벗어나면 패스)
        if (targetDate < today || targetDate > tillWhen) {
          Logger.log("   -> 마감 범위를 벗어난 날짜라 건너뜁니다: " + date + " (코드: " + group_code + ")");
          continue;
        }

        Logger.log((i + 1) + "번째 줄 처리 중 - 날짜: " + date + " | 코드: " + group_code);

        var startTime = new Date(targetDate.setHours(0, 0, 0, 0));
        var endTime = new Date(targetDate.setHours(23, 59, 59, 999));    
        var events = dayCalendar.getEvents(startTime, endTime);  

        // 중복 인원이 있는지부터 확인 (여기서부터 새로 봐야 함)
        var samePersonExists = false;
        for (var k = 0; k < events.length; k++) {
          var event = events[k];  
          title = event.getTitle()          
          var oldDescription = event.getDescription();

          if (oldDescription.includes(name) && oldDescription.includes(phone.slice(0, -1))) {
            samePersonExists = true;
            // 중복 인물의 인원수만 변경

            // const pattern = "(" + name + "\\s+)(.*?)(\\s+" + phone + ")"; 
            // const regex = new RegExp(pattern); 

            // const result = oldDescription.replace(regex, '\$1' + adt + "\$3");

            // console.log("oldDescription: " + oldDescription); 
            // break;
          }
        }

        console.log(name + date + adt); 

        // GOR, ZGOR 의 경우, 만약 자리가 남는 투어가 없다면 일정 하나를 새로 만들어야 함
        if (group_code == 'GOR') checkIfThereIsGORandCreate(group_code, events, dayCalendar, adt, chd, inf, date); 
        else if (group_code == 'ZGOR')  checkIfThereIsZGORandCreate(group_code, events, dayCalendar, adt, chd, inf, date); 
        else checkIfThereIsOTHERSandCreate(group_code, events, dayCalendar, adt, chd, inf, date); 
      
        var flag = false;

        for (var k = 0; k < events.length; k++) {

          if (samePersonExists) {
            console.log("같은 사람이 있어서 캘린더 정상여부는 False로 남겨두고 skip");
            break;
          } 

          var event = events[k];  
          title = event.getTitle()          
          var oldDescription = event.getDescription();

          if (title.includes('ZGOR')) {
            console.log("GROUP CODE : ZGOR")
            pax = readTitleReturnNumber(title)

            total_pax = pax + Number(adt) + Number(chd) + Number(inf);
            if (total_pax > 10) {
              continue;
            }
            flag = true; 
          }

          else if (title.includes('GOR')) {
            pax = readTitleReturnNumber(title)
            total_pax = pax + Number(adt) + Number(chd) + Number(inf); 
            console.log('total_pax: ' + total_pax); 
            if (total_pax > 48) {
              continue;
            }
            flag = true; 
          }

          Logger.log("name: " + name + " phone: " + phone);

          if (oldDescription.includes(name) && oldDescription.includes(phone.slice(0, -1))) {
            Logger.log("이미 있어서 건너뜀!");
            continue;
          }

          var peopleText = '';

          if ((group_code == "PB" || group_code == "PI") && title.includes('[PP')) {
            Logger.log("event.getTitle(): " + title);
          } else if (!event.getTitle().includes('[' + group_code)) {
            Logger.log("event.getTitle(): continue " + title);
            continue;
          }

          if (adt && adt != 0 && adt != '0') peopleText += adt + 'A ';
          if (chd && chd != 0 && chd != '0') peopleText += chd + 'C ';
          if (inf && inf != 0 && inf != '0') peopleText += inf + 'F ';

          var newText = platform + ' ' + name + ' ' + peopleText + phone;

          var updatedDescription = '';

          if (title.includes('[PP')) {

            var pbRegex = /\*PB[\s=\-_]*/;
            var piRegex = /\*PI[\s=\-_]*/;
            var ppRegex = /\*PP[\s=\-_]*/;

            if (title.includes('[PPT') && group_code == 'PP') continue;

            flag = true; 
            if (group_code == "PB" && oldDescription.match(piRegex)) {
              // PB 는 *PI=== 위로 올라가야 함.
              var [first, second] = oldDescription.split(piRegex);
              updatedDescription = first.trim() + '\n' + newText + '\n*PI=====================\n' + second.trim() + '\n';
            } else if (group_code == "PI" && oldDescription.match(piRegex)) {
              // PI 는 맨 아래로 내려가야 함.
              var [first, second] = oldDescription.split(piRegex);
              updatedDescription = first.trim() + '\n*PI=====================\n' + second.trim() + '\n' + newText + '\n';
            } else if (group_code == "PP" && oldDescription.match(pbRegex)) {
              // PP 는 *PB=== 위로 올라가야 함.
              var [first, second] = oldDescription.split(pbRegex);
              updatedDescription = first.trim() + '\n' + newText + '\n*PB=====================\n' + second.trim() +'\n';
            } else {
              updatedDescription = oldDescription ? oldDescription.trim() + "\n" + newText : newText;
            }

          } else if (title.includes('[ZGOR')) {
            flag = true; 
            updatedDescription = oldDescription ? oldDescription.trim() + "\n" + "*" + newText : "*" + newText;
          } else {
            flag = true; 
            updatedDescription = oldDescription ? oldDescription.trim() + "\n" + newText : newText;
          }

          console.log("updatedDescription: " + updatedDescription); 


          // 설명 및 제목 변경 주석 해제(필요시 주석 풀고 사용)
          event.setDescription(updatedDescription);

          updateEventTitle(event, updatedDescription, group_code);
          sheet.getRange(i + 1, targetColumnIndex + 1).setValue(true);

          if (flag) break;

        }
      }      
    }

}

