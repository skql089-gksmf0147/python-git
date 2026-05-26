let data={}

let rows=["movie","drama","variety"]

let currentRow=0

let currentIndex=0



fetch("/media.json")

.then(r=>r.json())

.then(json=>{

data=json

render()

setFocus()

})



function createCard(item){

const card=document.createElement("div")

card.className="card"

card.innerHTML=`
<img src="${item.thumb}">
<div class="title">${item.title}</div>
`

card.onclick=()=>{

const url=item.url || item.video

if(url){

window.open(url,"_blank","noopener")

}else{

alert("영상 주소 없음")

}

}

return card
}



function render(){

rows.forEach(row=>{

let container=document.getElementById(row)

container.innerHTML=""



let list=data[row]||[]



list.forEach(item=>{

container.appendChild(createCard(item))

})

})

}



function setFocus(){

document.querySelectorAll(".card").forEach(c=>c.classList.remove("focus"))



let row=document.getElementById(rows[currentRow])

let cards=row.querySelectorAll(".card")



if(cards.length===0)return



if(currentIndex>=cards.length)currentIndex=cards.length-1



cards[currentIndex].classList.add("focus")



cards[currentIndex].scrollIntoView({

behavior:"smooth",

inline:"center"

})

}



document.addEventListener("keydown",e=>{



let row=document.getElementById(rows[currentRow])

let cards=row.querySelectorAll(".card")



switch(e.key){



case "ArrowRight":

if(currentIndex<cards.length-1)currentIndex++

break



case "ArrowLeft":

if(currentIndex>0)currentIndex--

break



case "ArrowDown":

if(currentRow<rows.length-1){

currentRow++

currentIndex=0

}

break



case "ArrowUp":

if(currentRow>0){

currentRow--

currentIndex=0

}

break



case "Enter":

cards[currentIndex].click()

break



}



setFocus()



})