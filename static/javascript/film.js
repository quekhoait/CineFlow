function cardFilm(poster, content, flag){
return `
    <div class="flex-none w-[240px]">
        <div class="flex flex-col items-center bg-[#F3F3F3] rounded-[2rem] border-2 border-gray-200 shadow-sm py-2 px-1 w-full">
            <div class="w-full aspect-[3/4] overflow-hidden rounded-[1.5rem] shadow-lg border-2 border-white mb-6">
                <img src="${poster}" alt="Movie Poster" class="w-full h-full object-cover">
            </div>
            <div class="flex items-center justify-center space-x-2 bg-[#7D7D7D] rounded-full px-2 py-2 w-full border border-gray-400">
                ${ flag ? ' <span class="text-white text-lg font-medium">Khởi chiếu</span>' : "" }
                <div class="flex items-baseline space-x-1">
                    <span class="text-[#FFD700] text-lg font-medium">${content}</span>
                </div>
            </div>
        </div>
    </div>
`
}

function getFilmNowShowing(){
    const film = document.getElementById('slider-1')
   fetch('/api/film/list/now-showing')
        .then(res=>res.json())
        .then(data=>{
            let html = '';
            data.data.forEach(movie => {
                    html += cardFilm(movie.poster, movie.release_date, true);
                });
            film.innerHTML = html
        })
        .catch(err => console.error(err));
}

function getFilmReleaseShowing(){
    const film = document.getElementById('slider-2')
   fetch('/api/film/list/release-showing')
        .then(res=>res.json())
        .then(data=>{
            let html = '';
            console.log(data)
            data.data.forEach(movie => {
                    html += cardFilm(movie.poster, movie.title, false);
                });
            film.innerHTML = html
        })
        .catch(err => console.error(err));
}


getFilmNowShowing()
getFilmReleaseShowing()