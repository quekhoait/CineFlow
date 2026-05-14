from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


def open_momo_and_edit(pay_url):

    service = Service(executable_path="D:\Project\CineFlow\.venv\chromedriver.exe")
    print("hiihii")
    driver = webdriver.Chrome(service=service)
    driver.get(pay_url)


    # đợi render
    time.sleep(5)

    # inject javascript sửa countdown
    driver.execute_script("""

    setInterval(() => {

        const expireBox =
            document.querySelector('.time-expire-text');

        if(expireBox){

            expireBox.innerHTML = `

                <div style="
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                    width:100%;
                ">

                    <div style="
                        font-size:22px;
                        color:#d82d8b;
                        font-weight:bold;
                        margin-bottom:10px;
                    ">
                        Vé sẽ giữ trong
                    </div>

                    <div id="custom-timer"
                        style="
                        font-size:50px;
                        color:red;
                        font-weight:bold;
                    ">
                        10:00
                    </div>

                </div>
            `;

            // tránh tạo nhiều interval
            if(!window.customTimerStarted){

                window.customTimerStarted = true;

                let time = 600;

                setInterval(() => {

                    let min = Math.floor(time / 60);
                    let sec = time % 60;

                    const timer =
                        document.getElementById("custom-timer");

                    if(timer){

                        timer.innerText =
                            `${String(min).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;

                    }

                    time--;

                }, 1000);
            }
        }

    }, 1000);

    """)