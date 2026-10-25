function onOpen() {
  const ui = SpreadsheetApp.getUi(); 

  ui.createMenu('캘린더 검사')
    .addItem('검사 시작', 'eventValidation')
    .addToUi();

  ui.createMenu('캘린더 업데이트')
    .addItem('업데이트 시작', 'fromSheetToCalendar')
    .addToUi(); 
}

function doGet(e) {

  const action = e.parameter.action; 

  try {
    if (action == 'validate') {
      eventValidation(); 
      return ContentService.createTextOutput("캘린더 검사가 성공적으로 완료되었습니다. ")
    } else if (action == 'update') {
      fromSheetToCalendar(); 
      return ContentService.createTextOutput("캘런더 업데이트가 성공적으로 완료되었습니다. (validate 또는 update)");
    } else {
      return ContentService.createTextOutput("올바른 명령(action)을 입력해주세요. ")
    } 
  } catch(error) {
    return ContentService.createTextOutput("실행 중 오류가 발생했습니다: " + error.toString()); 
  }

}