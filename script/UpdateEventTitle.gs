// 데이터 추가 후 해당 일정의 제목을 인원수에 맞게 변경. 
function updateEventTitle(event, updatedDescription, group_code) {
  if (!group_code) return;

  var mySectionText = "";
  var desc = updatedDescription || "";

  // PP, PB, PI 뒤에 숫자가 붙어있어도 PP 패밀리로 인식 (예: PB1, PI2, PP1)
  var baseCode = group_code.replace(/\d+$/g, '').toUpperCase();
  var isPPFamily = (baseCode === "PP" || baseCode === "PB" || baseCode === "PI");

  if (isPPFamily) {
    // 본문 안에서 *PB, *PB1, *PI, *PI2, *PP 등의 구분자 위치 검색
    var pbRegex = /\*PB\d*[\s=\-_]*/i;
    var piRegex = /\*PI\d*[\s=\-_]*/i;
    var ppRegex = /\*PP\d*[\s=\-_]*/i;

    var pbIdx = desc.search(pbRegex);
    var piIdx = desc.search(piRegex);
    var ppIdx = desc.search(ppRegex);

    var sections = [
      { code: "PB", start: pbIdx !== -1 ? pbIdx : Infinity },
      { code: "PI", start: piIdx !== -1 ? piIdx : Infinity },
      { code: "PP", start: ppIdx !== -1 ? ppIdx : Infinity }
    ];

    // 본문 내 등장 위치 순서대로 정렬
    sections.sort(function(a, b) { return a.start - b.start; });

    var myOrderIdx = -1;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].code === baseCode) { 
        myOrderIdx = i; 
        break; 
      }
    }

    if (myOrderIdx !== -1 && sections[myOrderIdx].start !== Infinity) {
      var myStart = sections[myOrderIdx].start;
      var myEnd = desc.length;
      if (myOrderIdx + 1 < sections.length && sections[myOrderIdx + 1].start !== Infinity) {
        myEnd = sections[myOrderIdx + 1].start;
      }
      mySectionText = desc.substring(myStart, myEnd);
    } else {
      mySectionText = desc;
    }
  } else {
    // 일반 그룹코드 (GOR, ZGOR 등) - 해당 *group_code 섹션부터 다음 *그룹코드 전까지 잘라냄
    var myStartRegex = new RegExp('\\*' + group_code + '\\b', 'i');
    var matchPos = desc.search(myStartRegex);
    
    if (matchPos !== -1) {
      var afterText = desc.substring(matchPos);
      var nextHeaderMatch = afterText.substring(1).search(/\n\*[A-Za-z0-9]+/);
      if (nextHeaderMatch !== -1) {
        mySectionText = afterText.substring(0, nextHeaderMatch + 1);
      } else {
        mySectionText = afterText;
      }
    } else {
      mySectionText = desc;
    }

  }

  // A(성인), C(아동), F(유아) 수량 매칭 (대소문자 무시)
  var matchesA = mySectionText.match(/\b\d+A(?![a-zA-Z])/gi); 
  var matchesC = mySectionText.match(/\b\d+C(?![a-zA-Z])/gi); 
  var matchesF = mySectionText.match(/\b\d+F(?![a-zA-Z])/gi); 

  var totalA = 0, totalC = 0, totalF = 0;

  if (matchesA) { for (var m = 0; m < matchesA.length; m++) totalA += parseInt(matchesA[m], 10); }
  if (matchesC) { for (var m = 0; m < matchesC.length; m++) totalC += parseInt(matchesC[m], 10); }
  if (matchesF) { for (var m = 0; m < matchesF.length; m++) totalF += parseInt(matchesF[m], 10); }

  var resultTextList = [];
  if (totalA > 0) resultTextList.push(totalA + 'A');
  if (totalC > 0) resultTextList.push(totalC + 'C');
  if (totalF > 0) resultTextList.push(totalF + 'F');
  
  var newTotalText = resultTextList.join(' '); 

  var oldTitle = event.getTitle(); 
  var newTitle = "";

  var escapedCode = group_code.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'); 
  
  // ZGOR 뒤에 숫자가 붙은 [ZGOR1], [ZGOR2] 형태까지 모두 감지하는 정규식 (\d* 추가)
  var exactBracketRegex = new RegExp('\\[\\s*' + escapedCode + '\\d*(?:\\/[^\\]]+)?\\s*\\]', 'i');

  if (exactBracketRegex.test(oldTitle)) {
    // 기존 태그([ZGOR1]) 형태는 그대로 유지하면서 뒤의 수량만 newTotalText로 교체
    var targetPattern = new RegExp('(\\[\\s*' + escapedCode + '\\d*(?:\\/[^\\]]+)?\\s*\\])(?:\\s*\\b\\d+[a-zA-Z]\\b)*', 'gi');
    
    newTitle = oldTitle.replace(targetPattern, function(match, p1) {
      return newTotalText ? p1 + ' ' + newTotalText : p1;
    });
  } else {
    var tagToAdd = "[" + group_code + "]" + (newTotalText ? " " + newTotalText : "");
    newTitle = oldTitle + " " + tagToAdd;
  }

  newTitle = newTitle.replace(/\s+/g, ' ').trim();
  event.setTitle(newTitle); // 테스트 후 실제 반영 시 주석 해제
  Logger.log("   => [" + group_code + "] 정산 완료 -> 변경 후 제목: [" + newTitle + "]");

}