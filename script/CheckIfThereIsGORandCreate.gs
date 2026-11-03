// 조건에 맞는 GOR 일정이 이미 해당 날짜에 생성되어 있는지 확인. 없다면 새로 만들기. 
function checkIfThereIsGORandCreate(group_code, events, dayCalendar, adt, chd, inf, itineraryDate) {
  
  var hasToCreateNewGOR = true; 
  var countGOR = 0; 

  if (group_code == 'GOR') {
    for (var k = 0; k < events.length; k++) {

      var event = events[k]; 
      title = event.getTitle(); 

      var adtNum = adt ? Number(adt) : 0; 
      var chdNum = chd ? Number(chd) : 0; 

      if (title.includes('[GOR')) {
        prevPax = readTitleReturnNumber(title); 

        countGOR += 1; 

        sumGOR = prevPax + adtNum + chdNum; 

        if (sumGOR <= 48) hasToCreateNewGOR = false; 
      }
    }
  }

  if (hasToCreateNewGOR && group_code == 'GOR') {

    if (countGOR == 0) {
      countGOR = ''; 
    } else {
      countGOR += 1; 
    }

    const event = dayCalendar.createAllDayEvent("[GOR" + countGOR + "]", itineraryDate); 
    addDefaultGuests(event); 

    console.log("GOR 캘린더 생성 중..."); 
    events.push(event); 
    Utilities.sleep(1000); 
    console.log("GOR 캘린더 생성 완료"); 
  }
}
