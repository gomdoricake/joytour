// 캘린더 검사
function eventValidation() {
  // 1. 고유 ID로 스프레드시트 가져오기
  const ss = SpreadsheetApp.openById("1ZM4YqH-g6YMzIy3gS7GW3bhDhpQOp3qYh2mRGEHXSGo");
  const sheet = ss.getSheetByName("예약 리스트");
  
  // 2. 캘린더 가져오기
  const calendar = CalendarApp.getCalendarById("day@joystudytour.com.au");

  const data = sheet.getDataRange().getValues(); // 시트 데이터 가져오기
  const headers = data[0]; // 첫 번째 행을 헤더로 사용
  const rows = data.slice(1); // 나머지 데이터 처리
  
  const today = new Date();
  const oneYearLater = new Date();
  oneYearLater.setFullYear(today.getFullYear() + 1);

  // 헤더에서 각 열의 인덱스 찾기
  const colIndex = {
    name: headers.indexOf("이름"),
    travelDates: [
      headers.indexOf("여행일1"),
      headers.indexOf("여행일2"),
      headers.indexOf("여행일3"),
      headers.indexOf("여행일4"),
    ],
    travelOptions: [
      headers.indexOf("옵션1"),
      headers.indexOf("옵션2"),
      headers.indexOf("옵션3"),
      headers.indexOf("옵션4"),
    ],
    travelStartDate: headers.indexOf("시작"),
    travelEndDate: headers.indexOf("종료"),
    isValidated: headers.indexOf("캘린더 정상 여부"),
    isCancled: headers.indexOf("취소")
  };

  // 옵션 코드 매핑
  const optionCodeMap = {
    "그레이트오션로드": "GOR",
    "퍼핑빌리": "PB",
    "필립아일랜드": "PI",
    "퍼핑+필립": "PP",
    "모닝턴": "MON",
    "아침 모닝턴": "AMON",
    "오후 모닝턴": "PMON",
    "시티": "CT",
    "소규모 그레이트오션로드": "ZGOR",
    "와이너리": "WN",
    "그램피언즈": "GP",
    "소버린 힐": "SOV"
  };

  const batchSize = 50; // 한 번에 처리할 행의 수
  let startRow = 0;

  try {
    while (startRow < rows.length) {
      const batchRows = rows.slice(startRow, startRow + batchSize);
      
      batchRows.forEach((row, batchIndex) => {
        const rowIndex = startRow + batchIndex;
        const sheetRowNum = rowIndex + 2; // 
        
        // 시작일/종료일 데이터가 아예 없는 경우 FALSE 처리
        if (!row[colIndex.travelStartDate] || !row[colIndex.travelEndDate]) {
          Logger.log(`[${sheetRowNum}행] 시작일 또는 종료일 칸이 비어있어 FALSE 처리 후 건너뜁니다.`);
          const validationCell = sheet.getRange(sheetRowNum, colIndex.isValidated + 1);
          validationCell.setValue("FALSE");
          return;
        }     

        const name = row[colIndex.name];
        const isCancled = row[colIndex.isCancled];
      

        const startTravelDate = new Date(row[colIndex.travelStartDate]);
        startTravelDate.setDate(startTravelDate.getDate() - 1);
        const endTravelDate = new Date(row[colIndex.travelEndDate]);

        Logger.log(`[${sheetRowNum}행 진단] 이름: "${name}", 취소칸: "${isCancled}", 시작일: "${startTravelDate.toDateString()}", 종료일: "${endTravelDate.toDateString()}"`);
        endTravelDate.setDate(endTravelDate.getDate() + 1);
      
        let isValid = true; 

        if (name && !isCancled) { 
          // 1. 구글 캘린더에서 사용자 이름으로 이벤트 검색
          const events = calendar.getEvents(startTravelDate, endTravelDate, { search: name });

          // 2. 검색 결과와 시트 데이터 비교
          for (let i = 0; i < colIndex.travelDates.length; i++) {
            const travelDate = row[colIndex.travelDates[i]];
            const travelOption = row[colIndex.travelOptions[i]];
            const travelCode = optionCodeMap[travelOption];

            if (!travelDate || !travelOption) continue;

            const checkToday = new Date();
            checkToday.setHours(0,0,0,0);

            // 이미 완료된 여행인 경우 검사 패스
            if (new Date(travelDate) < checkToday) continue;

            Logger.log(`시트코드: ${travelCode}, 여행일: ${new Date(travelDate).toDateString()}`);

            const matchingEvent = events.find(event => {
              const title = event.getTitle();
              const eventDate = event.getStartTime();
              
              return (
                title.includes(travelCode) &&
                eventDate.toDateString() === new Date(travelDate).toDateString()
              );
            });

            if (!matchingEvent) {
              isValid = false; 
              break;
            }
          }
        } 

        // 3. 결과 기록
        const validationCell = sheet.getRange(sheetRowNum, colIndex.isValidated + 1);
        validationCell.setValue(isValid ? "TRUE" : "FALSE");
      });

      // 과부하 방지 대기
      Utilities.sleep(2000); 
      startRow += batchSize; 
    }
  } catch (error) {
    Logger.log(`Error processing rows: ${error.message}`);
  }

  try {
    const filterColumnIndex = colIndex.isValidated + 1;
    
    // 기존 필터가 켜져 있다면 깨끗하게 제거
    if (sheet.getFilter()) {
      sheet.getFilter().remove();
    }

    // 데이터가 있는 전체 영역에 새 필터 생성
    sheet.getRange(1, 1, sheet.getLastRow(), headers.length).createFilter();
    const filter = sheet.getFilter();
    
    if (filter) {
      // 캘린더 정상 여부 열에서 "FALSE"인 것만 보여주도록 필터링 규칙 삽입
      const criteria = SpreadsheetApp.newFilterCriteria().whenTextEqualTo("FALSE").build();
      filter.setColumnFilterCriteria(filterColumnIndex, criteria);
    }
  } catch (fError) {
    Logger.log(`필터 생성 중 오류: ${fError.message}`);
  }
}

