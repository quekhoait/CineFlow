<<<<<<< HEAD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
};

let selectedBranchId = 1;
let selectedDate =formatDate(new Date())


function cardDate(day_month, day_name) {
    const isActive = (day_name === selectedDate);
    const activeClass = isActive
        ? "bg-red-800 text-white border-red-800"
        : "bg-white text-gray-800 border-gray-100";

    return `
     <button onclick="handleSelectDate(this, '${day_name}')"
             class="date-item ${activeClass} flex-none flex flex-col items-center justify-center w-24 h-20 rounded-2xl border transition-all">
        <span class="text-sm font-medium">${day_month}</span>
        <span class="text-xs italic">${day_name}</span>
    </button>
   `;
}

function loadDate() {
    const days = [
        "Chủ nhật", "Thứ 2", "Thứ 3",
        "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"
    ];
    const today = new Date();
    const res = [];
    let dateString = ''
    for (let i = 0; i < 7; i++) {
        const nextDate = new Date(today);
        nextDate.setDate(today.getDate() + i);
        dateString = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}-${String(nextDate.getDate()).padStart(2, '0')}`;
        let dayName = "";
        if (i === 0) {
            dayName = "Hôm nay";
        } else {
            dayName = days[nextDate.getDay()];
        }
        res.push({
            label: dayName,
            date: dateString,
        });
    }
    document.getElementById('date_picker').innerHTML = res.map(item => cardDate(item.label, item.date)).join('');
    }


function branch(cities) {
    return `
    <div class="bg-white/60 backdrop-blur-md rounded-[2rem] p-6 shadow-sm border border-white w-full max-w-[350px]">
        <h3 class="italic text-right mb-4 text-gray-600">Chi nhánh</h3>
        ${cities.map(city => `
            <div class="mb-6">
                <h4 class="text-purple-800 font-bold mb-3 border-b border-purple-200 pb-1">${city.province}</h4>
                <div class="space-y-2">
                    ${city.location.map(item => `
                        <button onclick="handleSelectBranch(this,'${item.id}')" class="btn-branch w-full text-left px-4 py-2 rounded-xl bg-white border border-gray-100 hover:bg-purple-50 transition-colors shadow-sm text-sm">
                            ${item.name}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    </div>
    `;
}

function renderAddress(cinema_name, address){
    return `
        <p class="font-bold text-gray-800 text-lg">${cinema_name}</p>
        <p class="text-sm text-gray-500">${address}</p>
    `
    }

function renderFilm(movies) {
    if (!movies || movies.length === 0) {
        return '<p class="text-center text-gray-500 py-10">Hiện chưa có lịch chiếu cho ngày này.</p>';
    }
    return movies.map(movie => `
        <div class="bg-white/80 backdrop-blur-md rounded-[2.5rem] p-6 flex gap-6 shadow-sm mb-6 border border-white">
            <div class="w-32 h-48 flex-none rounded-2xl overflow-hidden relative shadow-lg">
                <span class="absolute top-2 left-2 bg-red-600/80 text-white text-[10px] px-2 py-1 rounded-lg font-bold">T${movie.age_limit}</span>
                <img src="${movie.poster}" class="w-full h-full object-cover">
            </div>
            <div class="flex-grow">
                <h3 class="text-xl font-bold text-gray-800 mb-1">${movie.title}</h3>
                <p class="text-sm text-gray-400 mb-4">${movie.duration} phút | ${movie.genre}</p>

                <div class="grid grid-cols-4 sm:grid-cols-6 gap-2">
                    ${movie.schedule.map(item => {
                       const time = formatTime(item.start_time)
                        return `
                            <button onclick="selectTime('${item.id}')" class="bg-white border border-gray-100 py-2 rounded-xl text-xs font-bold text-purple-700 hover:bg-purple-600 hover:text-white transition-all shadow-sm">
                                ${time}
                            </button>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function loadBranch(){
    fetch('/api/cinemas')
    .then(res=>res.json())
    .then(res=>{
        const data = res.data;
        console.log(data)
        document.getElementById("branch_location").innerHTML = branch(data)
        const firstBranchBtn = document.querySelector('.btn-branch');
        selectedBranchId = 1
        handleSelectBranch(firstBranchBtn, selectedBranchId)
    })
}

function handleSelectBranch(element, id) {
  document.querySelectorAll('.btn-branch').forEach(btn => {
        btn.classList.remove('bg-red-800', 'text-white');
        btn.classList.add('bg-white', 'text-gray-800');
    });
    if(element){
        element.classList.remove('bg-white', 'text-gray-800');
        element.classList.add('bg-red-800', 'text-white');
    }
    fetch(`/api/cinemas/${id}`)
    .then(res=>res.json())
    .then(res=>{
        if(res.status==="success"){
            document.getElementById("address_cinema").innerHTML = renderAddress(res.data.name, res.data.address)
        }else{
            console.error("Lỗi API:", res.message);
        }
    })
    selectedBranchId = id;
    checkResult();
}

function handleSelectDate(element, date) {
  document.querySelectorAll('.date-item').forEach(btn => {
        btn.classList.remove('bg-red-800', 'text-white');
        btn.classList.add('bg-white', 'text-gray-800');
    });
    if(element){
        element.classList.remove('bg-white', 'text-gray-800');
        element.classList.add('bg-red-800', 'text-white');
    }
    selectedDate = date;
    checkResult();
}

function checkResult() {
    if (selectedBranchId && selectedDate) {
          fetch(`/api/cinemas/${selectedBranchId}/films?date=${selectedDate}`)
            .then(res => res.json())
            .then(res => {
                if (res.status === "success") {
                    document.getElementById('schedule-film').innerHTML =  renderFilm(res.data)
                } else {
                    console.error("Lỗi API:", res.message);
                }
            })
            .catch(err => console.error("Lỗi kết nối:", err));
    }
}
loadDate()
loadBranch()
checkResult()


function loadSeat(movie) {
    return `
    <div class="space-y-6 w-full">
        <div class="bg-white rounded-[2rem] p-5 shadow-lg flex gap-4 border border-gray-100">
            <img src="{{ movie.poster }}" class="w-24 h-32 rounded-xl object-cover">
            <div class="text-sm">
                <h3 class="font-bold text-lg leading-tight">{{ movie.title }}</h3>
                <p class="text-gray-500 mt-1">{{ movie.theater }}</p>
                <p class="text-gray-500">Phòng: {{ movie.room }}</p>
                <p class="text-gray-500">Ghế: {{ movie.seats_selected | join(', ') }}</p>
                <p class="text-gray-500">Suất: {{ movie.time }}</p>
            </div>
        </div>
    
        <div class="bg-white rounded-[2rem] p-8 shadow-lg border border-gray-100 text-center">
            <p class="text-gray-400 text-xl uppercase tracking-widest">Tổng đơn hàng</p>
            <h2 class="text-xl font-bold my-4">{{ "{:,.0f}".format(total_price) }}đ</h2>
           {% if is_open %}
            <button class="w-full bg-[#98E2E7] hover:bg-[#7bcad0] text-gray-700 font-bold py-3 rounded-full transition-colors uppercase text-sm">
                Tiếp tục
            </button>
            {% endif %}
        </div>
    </div>
    `;
}

function selectTime(id){
    console.log(id) //id suâất chiếu
}