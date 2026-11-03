// 조건에 맞는 ZGOR 일정이 해당 날짜에 이미 있는지 확인. 없다면 새로 생성. 
function checkIfThereIsZGORandCreate(group_code, events, dayCalendar, adt, chd, inf, itineraryDate) {
  
  var hasToCreateNewZGOR = true; 
  var countZGOR = 0; 

  if (group_code == 'ZGOR') {
    for (var k = 0; k < events.length; k++) {

      var event = events[k]; 
      title = event.getTitle(); 

      var adtNum = adt ? Number(adt) : 0; 
      var chdNum = chd ? Number(chd) : 0; 

      if (title.includes('[ZGOR')) {
        prevPax = readTitleReturnNumber(title); 

        countZGOR += 1; 

        sumZGOR = prevPax + adtNum + chdNum; 

        if (sumZGOR <= 10) {
          hasToCreateNewZGOR = false; 
        }
      }
    }
  }

  if (hasToCreateNewZGOR && group_code == 'ZGOR') {

    if (countZGOR == 0) {
      countZGOR = ''; 
    } else {
      countZGOR += 1; 
    }

    const event = dayCalendar.createAllDayEvent("[ZGOR" + countZGOR + "]", itineraryDate); 
    addDefaultGuests(event); 

    console.log("ZGOR 캘린더 생성 중..."); 
    events.push(event); 
    Utilities.sleep(1000); 
    console.log("ZGOR 캘린더 생성 완료"); 
  }
}
