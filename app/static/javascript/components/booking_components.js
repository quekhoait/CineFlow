import {loadHTML} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";



export function handleSelectShow(id) {
   sessionStorage.setItem('selectedShowId', id);
    window.location.href = `/booking-seat`;
}

export async function getShowSeat(){
    // const token =  await localStorage.getItem('token');
    const id = sessionStorage.getItem('selectedShowId');
    await fetch(`/api/shows/${id}`, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            // 'Authorization': `Bearer ${token}`
        }
    }).then(async res => {
        if (res.status === 200) {
            let result = await res.json();
            return result.data
        } else {
            const errorData = await res.json();
            showAlert("error", "Lỗi hệ thống", errorData.message || "Không thể tải danh sách chi nhánh");
        }
    })
}

export async function loadBookingSummary(){
    const data = await getShowSeat()
    console.log(data)
        const template = await loadHTML("/templates/components/booking_seat/booking_summary.html")
    const info_film = template.body.innerHTML
    let film = ''
        const container = document.getElementById("booking_summary");
        if (container) {
                film = info_film.replace('{{poster}}', data.show_info.poster)
                    .replace("{{title}}", data.show_info.film_title)
                .replace("{{room}}", data.show_info.room_name)
                .replace("{{seats_selected}}", "1") ////////////
                .replace("{{time}}", data.show_info.start_time)

            container.innerHTML = film
            console.log(film)

    } else {
        let errorDetail = result.message || "Không có dữ liệu chi nhánh";
        showAlert("error", "Lỗi dữ liệu", errorDetail);
    }
}

export async function loadSeat() {
            const data =await getShowSeat()
            const seats = data.seats;
            const container = document.getElementById("seat_container");
            if (container && seats) {
                const rows = Object.groupBy(seats, seat => seat.row);
                const maxCols = Math.max(...seats.map(s => s.col));
                let finalHTML = "";
                Object.entries(rows).sort().forEach(([label, seatsInRow]) => {
                    let rowSeatsHTML = "";
                    for (let col = 1; col <= maxCols; col++) {
                        const seat = seatsInRow.find(s => s.col === col);
                        if (seat) {
                            const isCouple = seat.type === "COUPLE";
                            const isBooked = seat.is_booked === true;
                            let seatClass = isCouple ? "w-16 bg-[#F8A4FF]" : "w-10 bg-white";
                            if (isBooked) {
                                seatClass = (isCouple ? "w-16" : "w-10") + " bg-[#A1A3A6] cursor-not-allowed opacity-60";
                            } else {
                                seatClass += " cursor-pointer hover:border-[#F1B400] hover:scale-105";
                            }
                            rowSeatsHTML += `
                                <div class="seat-item h-8 ${seatClass} border border-gray-200 rounded-md flex items-center justify-center text-[10px] font-bold transition-all shadow-sm"
                                     data-code="${seat.code}"
                                     data-booked="${isBooked}">
                                    ${seat.row}${seat.col}
                                </div>`;
                        } else {
                            rowSeatsHTML += `<div class="w-10 h-8"></div>`;
                        }
                    }
                    finalHTML += `
                        <div class="flex items-center gap-4 mb-3 justify-center">
                            <span class="w-6 text-xs font-bold text-gray-500 text-center">${label}</span>
                            <div class="flex gap-2">
                                ${rowSeatsHTML}
                            </div>
                            <span class="w-6 text-xs font-bold text-gray-500 text-center">${label}</span>
                        </div>`;
                });
                container.innerHTML = finalHTML;
            } else {
                console.error("Không tìm thấy container hoặc dữ liệu ghế trống");
            }

}
