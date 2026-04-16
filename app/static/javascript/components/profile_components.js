import {showAlert} from "../utils/alert.js";
import {showError} from "../utils/load.js";

export function loadProfile() {
    const infoLabels = document.querySelectorAll('span.info-text')
    const infoInput = document.querySelectorAll('input.info-input')
    const infoAva = document.querySelectorAll('.avatar-info')[0]
    fetch('/api/user/profile', {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        },
    }).then(async res => {
        let result = await res.json()
        let info = [result.data.full_name, result.data.email, result.data.username, result.data.phone_number]
        infoInput.forEach((input, i) => {
            input.value = info[i] !== undefined ? info[i] : ""
        })

        infoAva.src = result.data.avatar

        infoLabels.forEach((label, i) => {
            label.innerText = infoInput[i].value
        })
    })
}

export function updateProfile() {
    const updateBtn = document.getElementById('updateBtn');
    const editBtn = document.getElementById('editBtn');
    const infoLabels = document.querySelectorAll('span.info-text');
    const infoInputs = document.querySelectorAll('input.info-input');

    const avatarContainer = document.getElementById('avatarContainer');
    const avatarInput = document.getElementById('avatarInput');
    const avatarImg = document.querySelector('.avatar-info');
    const avatarOverlay = document.getElementById('avatarOverlay');

    let isEditing = false;

    updateBtn.addEventListener('click', () => {
        isEditing = true;
        editBtn.classList.remove('hidden');
        updateBtn.classList.add('hidden');

        infoLabels.forEach(label => label.classList.add('hidden'));
        infoInputs.forEach(input => input.classList.remove('hidden'));

        avatarContainer.classList.add('cursor-pointer');
    });

    avatarContainer.addEventListener('click', () => {
        if (isEditing) {
            avatarInput.click();
        }
    });

    avatarInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                avatarImg.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    editBtn.addEventListener('click', async () => {
        const formData = new FormData();

        infoInputs.forEach(input => {
            if (input.name !== 'email') {
                formData.append(input.name, input.value);
            }
        });

        if (avatarInput.files[0]) {
            formData.append('avatar', avatarInput.files[0]);
        }

        try {
            editBtn.innerText = 'Đang lưu...';
            editBtn.disabled = true;

            const response = await fetch('/api/user/profile', {
                method: 'PUT',
                credentials: 'include',
                body: formData,
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                showAlert('success', 'Profile', 'Update successful');

                infoInputs.forEach((input, i) => {
                    infoLabels[i].innerText = input.value;
                });

                isEditing = false;
                editBtn.classList.add('hidden');
                updateBtn.classList.remove('hidden');
                infoLabels.forEach(label => label.classList.remove('hidden'));
                infoInputs.forEach(input => input.classList.add('hidden'));
                avatarContainer.classList.remove('cursor-pointer');

                loadProfile();
            } else {
                const err = await response.json();
                showError('Profile', err)
            }
        } catch (error) {
            showAlert('error', 'Profile', 'Update failed')
        } finally {
            editBtn.innerText = 'Lưu';
            editBtn.disabled = false;
        }
    });
}