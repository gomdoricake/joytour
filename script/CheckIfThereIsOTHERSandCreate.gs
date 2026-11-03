// GOR, ZGOR 이 아닌 다른 일정들이 해당 날짜에 이미 있는지 확인. 없다면 새로 생성. 
function checkIfThereIsOTHERSandCreate(group_code, events, dayCalendar, adt, chd, inf, itineraryDate) {
  
  var hasToCreateNewOther = true; 

  for (k = 0; k < events.length; k++) {
    var event = events[k]; 
    var title = event.getTitle(); 

    if (title.includes('[' + group_code)) hasToCreateNewOther = false; 
  }

  if (hasToCreateNewOther) {
    const event = dayCalendar.createAllDayEvent("[" + group_code + "]", itineraryDate); 
    addDefaultGuests(event); 

    console.log(group_code + " 캘린더 생성 중..."); 
    events.push(event); 
    Utilities.sleep(1000); 
    console.log(group_code + " 캘린더 생성 완료"); 
  }
}
