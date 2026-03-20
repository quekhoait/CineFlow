/** Alert animation + style */
function showAlert(type, title, message) {
  const alertBox = document.getElementById("form_alert");
  const iconBox = document.getElementById("alert_icon");
  const textBox = document.getElementById("alert_text");

  // Reset tất cả style cũ
  alertBox.classList.remove(
    "bg-green-50","border-green-300","text-green-800",
    "bg-red-50","border-red-300","text-red-800",
    "bg-orange-50","border-orange-300","text-orange-800",
    "bg-blue-50","border-blue-300","text-blue-800"
  );

  iconBox.innerHTML = "";
  textBox.innerHTML = "";

  let bg = "", border = "", txt = "", icon = "";

  switch(type) {
    case "success":
      bg = "bg-green-50"; border = "border-green-300"; txt = "text-green-800";
      icon = `<i class="fas fa-check-circle text-green-500 text-2xl"></i>`;
      break;

    case "error":
      bg = "bg-red-50"; border = "border-red-300"; txt = "text-red-800";
      icon = `<i class="fas fa-times-circle text-red-500 text-2xl"></i>`;
      break;

    case "loading":
      bg = "bg-blue-50"; border = "border-blue-300"; txt = "text-blue-800";
      icon = `<i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i>`;
      break;

    default:
      bg = "bg-orange-50"; border = "border-orange-300"; txt = "text-orange-800";
      icon = `<i class="fas fa-exclamation-triangle text-orange-500 text-2xl"></i>`;
  }

  iconBox.innerHTML = icon;
  textBox.innerHTML = `
    <p class="font-bold mb-1">${title}</p>
    <p>${message}</p>
  `;
  alertBox.classList.add(bg, border, txt);
  alertBox.classList.remove("hidden");
  alertBox.style.opacity = "0";
  alertBox.style.transform = "translateX(15px)";

  setTimeout(() => {
    alertBox.style.transition = "0.3s ease";
    alertBox.style.opacity = "1";
    alertBox.style.transform = "translateX(0)";
  }, 10);

  // Tự động ẩn alert chỉ với success, error, warning
  if(type !== "loading") {
    setTimeout(() => {
      hideAlert();
    }, 5000);
  }
}

function hideAlert() {
  const alertBox = document.getElementById("form_alert");
  alertBox.style.opacity = "0";
  alertBox.style.transform = "translateX(15px)";

  setTimeout(() => {
    alertBox.classList.add("hidden");
  }, 300);
}


//?header
window.addEventListener('scroll', function() {
  const header = document.getElementById('header');
    console.log(header)
  if (window.scrollY > 50) {
      header.classList.remove(  "py-4");
    header.classList.add( 'shadow-[0px_3px_8px_rgba(0,0,0,0.24)]', "py-2.5");

  } else {
    header.classList.remove( 'shadow-[0px_3px_8px_rgba(0,0,0,0.24)]', "py-2.5");
    header.classList.add(  "py-4");
  }
});


 document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll(".nav-item");
    const currentPath = window.location.pathname;
    items.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add("bg-white", "shadow-sm", "text-gray-800", "font-medium");
            item.classList.remove("text-gray-500");
        } else {
            item.classList.add("text-gray-500");
            item.classList.remove("bg-white", "shadow-sm", "text-gray-800", "font-medium");
        }
    });
});





