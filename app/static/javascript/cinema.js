function cardDate(day_month, day_name){
   return `
     <button class="flex-none flex flex-col items-center justify-center w-24 h-20 rounded-2xl border transition-all">
        <span class="text-sm font-medium">${day_month}</span>
        <span class="text-xs italic">${day_name}</span>
    </button>
   `
 }



function loadDate() {
    const days = [
        "Chủ nhật", "Thứ 2", "Thứ 3",
        "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"
    ];
    const today = new Date();
    const res = [];
    for (let i = 0; i < 7; i++) {
        const nextDate = new Date(today);
        nextDate.setDate(today.getDate() + i);
        const dateString = `${nextDate.getDate()}/${nextDate.getMonth() + 1}`;
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
    document.getElementById('date_picker').innerHTML = res.map(item => cardDate(item.label, item.date));
    }
loadDate()

function branch(cities) {
    return `
    <div class="bg-white/60 backdrop-blur-md rounded-[2rem] p-6 shadow-sm border border-white w-full max-w-[350px]">
        <h3 class="italic text-right mb-4 text-gray-600">Chi nhánh</h3>
        ${cities.map(city => `
            <div class="mb-6">
                <h4 class="text-purple-800 font-bold mb-3 border-b border-purple-200 pb-1">${city.province}</h4>
                <div class="space-y-2">
                    ${city.location.map(item => `
                        <button onclick="handleBranch('${item.id}')" class="w-full text-left px-4 py-2 rounded-xl bg-white border border-gray-100 hover:bg-purple-50 transition-colors shadow-sm text-sm">
                            ${item.name}
                        </button>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    </div>
    `;
}

function loadBranch(){
    fetch('/api/cinema/list')
    .then(res=>res.json())
    .then(data=>{
        document.getElementById("branch_location").innerHTML = branch(data.data)
    })
}
loadBranch()

function handleBranch(id, date){
    
}