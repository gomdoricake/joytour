// 어카운트, 데이, 가이드 계정 권한 부여.
function addDefaultGuests(event) {
    const ACCOUNT_EMAIL = "account@joystudytour.com.au";
    const DAY_EMAIL = "day@joystudytour.com.au";
    const GUIDE_EMAIL = "guide@joystudytour.com.au";

    event.addGuest(DAY_EMAIL); 
    event.addGuest(ACCOUNT_EMAIL);
    event.addGuest(GUIDE_EMAIL); 
    event.setGuestsCanModify(true);
    event.setGuestsCanInviteOthers(true);
    event.setGuestsCanSeeGuests(true);
}