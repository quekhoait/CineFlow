import * as settingComponents from '../components/setting_components.js'

document.addEventListener("DOMContentLoaded", () => {
    window.switchTab = settingComponents.switchTab
    settingComponents.loadPriceSettings()
    settingComponents.updateBtn()
})