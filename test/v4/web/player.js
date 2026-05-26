const params=new URLSearchParams(location.search)

const url=params.get("video")

const frame=document.getElementById("playerFrame")

frame.src=url



// HOME 버튼

document.getElementById("homeBtn").onclick=function(){

location.href="index.html"

}



// ESC → 메인

document.addEventListener("keydown",function(e){

if(e.key==="Escape"){

location.href="index.html"

}

})



// 자동 전체화면

setTimeout(()=>{

document.documentElement.requestFullscreen()

},500)