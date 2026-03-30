document.addEventListener('DOMContentLoaded', () => {
    const editBtn = document.getElementById('editBtn');
    const infoTexts = document.querySelectorAll('.info-text');
    const infoInputs = document.querySelectorAll('.info-input');
    let isEditing = false;

    editBtn.addEventListener('click', () => {
        showAlert("success", "ok", "ok")
        isEditing = !isEditing;

        if (isEditing) {
            editBtn.innerText = 'Lưu';
            editBtn.classList.replace('bg-[#33CCFF]', 'bg-green-500');
            infoTexts.forEach(t => t.classList.add('hidden'));
            infoInputs.forEach(i => i.classList.remove('hidden'));
        } else {
            editBtn.innerText = 'Cập nhật';
            editBtn.classList.replace('bg-green-500', 'bg-[#33CCFF]');
            infoInputs.forEach((input, index) => {
                const newValue = input.value;
                infoTexts[index].innerText = newValue;
                input.classList.add('hidden');
                infoTexts[index].classList.remove('hidden');
            });
            console.log("Dữ liệu đã cập nhật thành công!");
        }
    });
});
