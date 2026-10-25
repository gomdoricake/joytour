// 캘린더 제목을 보고 이미 해당 일정에 몇명이 있는지 계산하여 반환. 
function readTitleReturnNumber(title) {
  const adtNumbers = title.match(/\d+(?=A)/gi) || [];
  const chdNumbers = title.match(/\d+(?=C)/gi) || []; 
  const infNumbers = title.match(/\d+(?=I)/gi) || []; 

  var sum = 0;

  for (const number of adtNumbers) {
    sum += Number(number);
  }

  for (const number of chdNumbers) {
    sum += Number(number); 
  }

  for (const number of infNumbers) {
    sum += Number(number); 
  }

  return sum;
}
