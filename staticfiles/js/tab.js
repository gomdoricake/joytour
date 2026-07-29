<script>
  document.addEventListener("DOMContentLoaded", function () {
    // 1. 저장된 스크롤 위치가 있다면 복원
    const scrollPosition = sessionStorage.getItem("scrollPosition");
    if (scrollPosition !== null) {
      window.scrollTo(0, parseInt(scrollPosition, 10));
      sessionStorage.removeItem("scrollPosition"); // 사용 후 삭제
    }

    // 2. 탭 버튼 클릭 시 현재 스크롤 Y축 위치 저장
    const tabLinks = document.querySelectorAll(".xero-tab-item");
    tabLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        sessionStorage.setItem("scrollPosition", window.scrollY);
      });
    });
  });
</script>