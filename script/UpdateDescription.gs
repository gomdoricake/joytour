// 캘린더 내용을 변경.
function updateDescription(oldDescription, group_code, newText) {

  var desc = oldDescription || "";
  var codeRegex = new RegExp('\\*' + group_code + '\\b', 'i');

  if (codeRegex.test(desc)) {

    var splitParts = desc.split(codeRegex);
    var firsttext = splitParts[0];
    var secondtext = splitParts.slice(1).join('*' + group_code);

    return firsttext + '\n*' + group_code + '\n' + newText + secondtext;
  } else {
    return desc ? desc + "\n\n*" + group_code + "\n" + newText : "*" + group_code + "\n" + newText;
  }

}
