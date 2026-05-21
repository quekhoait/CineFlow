import { showAlert } from "../utils/alert.js";
import { showError } from "../utils/load.js";
import fetchAPI from "../utils/apiClient.js";

export async function loadProfile() {
    try {
        const res = await fetchAPI('/api/user/profile', { method: 'GET' });

        if (res.ok && res.data) {
            const user = res.data.data || res.data;
            const infoAva = document.querySelector('.avatar-info');
            const infoLabels = document.querySelectorAll('span.info-text');
            const infoInputs = document.querySelectorAll('input.info-input');

            infoInputs.forEach((input, i) => {
                const key = input.name;
                const value = user[key] !== undefined && user[key] !== null ? user[key] : "";

                input.value = value;
                if (infoLabels[i]) infoLabels[i].innerText = value;
            });

            if (infoAva && user.avatar) {
                infoAva.src = user.avatar;
            }
        } else {
            showAlert("error", "Error", "Unable to load profile information.");
        }
    } catch (error) {
        showAlert("error", "Network Error", "Unable to connect to the server.");
    }
}

export function updateProfile() {
    const updateBtn = document.getElementById('updateBtn');
    const editBtn = document.getElementById('editBtn');
    const infoLabels = document.querySelectorAll('span.info-text');
    const infoInputs = document.querySelectorAll('input.info-input');

    const avatarContainer = document.getElementById('avatarContainer');
    const avatarInput = document.getElementById('avatarInput');
    const avatarImg = document.querySelector('.avatar-info');

    if (!updateBtn || !editBtn) return;

    let isEditing = false;
    updateBtn.onclick = () => {
        isEditing = true;
        editBtn.classList.remove('hidden');
        updateBtn.classList.add('hidden');

        infoLabels.forEach(label => label.classList.add('hidden'));
        infoInputs.forEach(input => input.classList.remove('hidden'));

        if (avatarContainer) avatarContainer.classList.add('cursor-pointer');
    };

    if (avatarContainer && avatarInput) {
        avatarContainer.onclick = () => {
            if (isEditing) avatarInput.click();
        };

        avatarInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file && avatarImg) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    avatarImg.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        };
    }

    editBtn.onclick = async () => {
        const formData = new FormData();

        infoInputs.forEach(input => {
            if (input.name && input.name !== 'email') {
                formData.append(input.name, input.value);
            }
        });

        if (avatarInput && avatarInput.files[0]) {
            formData.append('avatar', avatarInput.files[0]);
        }

        try {
            editBtn.innerText = 'Đang lưu...';
            editBtn.disabled = true;

            const res = await fetchAPI('/api/user/profile', {
                method: 'PUT',
                body: formData,
            });

            if (res.ok) {
                showAlert('success', 'Success', 'Profile updated successfully');

                infoInputs.forEach((input, i) => {
                    if (infoLabels[i]) infoLabels[i].innerText = input.value;
                });

                isEditing = false;
                editBtn.classList.add('hidden');
                updateBtn.classList.remove('hidden');
                infoLabels.forEach(label => label.classList.remove('hidden'));
                infoInputs.forEach(input => input.classList.add('hidden'));
                if (avatarContainer) avatarContainer.classList.remove('cursor-pointer');

            } else {
                showError('Profile', res.data || "Update failed");
            }
        } catch (error) {
            console.error("Error updating profile:", error);
            showAlert('error', 'Error', 'Unable to connect to the server');
        } finally {
            editBtn.innerText = 'Lưu';
            editBtn.disabled = false;
        }
    };
}