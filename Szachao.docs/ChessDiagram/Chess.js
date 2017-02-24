//==============================================
//Copyright. All rights reserved.
//Alexander Babichev (babichev$telpacific.com.au). 
//A fee (US$10) is required to use this script.
//==============================================

var white = ""
var black = ""

function bw(i,j){
var strF, intF, diff
		strF = i + j
		intF = parseInt(strF)
		diff = intF/2
		strF = "" + parseInt(diff)
		if (strF == String(diff)){
			return("b")
		}
		else{
			return("w")
		}
}


function reverseSort(a, b) 
{ 
   if(a > b) 
      return -1 
   if(a < b) 
      return 1 
   return 0 
} 


function chessDiagram(){
var bArr = black.split(",")
var wArr = white.split(",")
var set = new Array()
set = []
var n = 0
var m = ""

	for (i=0;i<wArr.length;i++){
		m = wArr[i]
		if (m.length == 2){
			wArr[i] = "P" + m	
		}
	}

	for (i=0;i<bArr.length;i++){
		m = bArr[i]
		if (m.length == 2){
			bArr[i] = "P" + m	
		}
	}

	for (i=0;i<wArr.length;i++){
		m = wArr[i]
		if (m.length == 3){
			set[n] = m + "w"	
			n = n + 1
		}
	}

	for (i=0;i<bArr.length;i++){
		m = bArr[i]
		if (m.length == 3){
			set[n] = m + "b"
			n = n + 1	
		}
	}

var ch1="",ch2="",ch3="",ch4=""
	for (i=0;i<set.length;i++){
		m = set[i]
		ch1 = m.charAt(0)
		ch2 = m.charAt(1)
		ch3 = m.charAt(2)
		ch4 = m.charAt(3)	

		switch(ch2){
			case 'a':
			ch2 = "8"
			break
			
			case 'b':
			ch2 = "7"
			break

			case 'c':
			ch2 = "6"
			break
			
			case 'd':
			ch2 = "5"
			break

			case 'e':
			ch2 = "4"
			break

			case 'f':
			ch2 = "3"
			break
			
			case 'g':
			ch2 = "2"
			break

			case 'h':
			ch2 = "1"
			break			
		}
		
		set[i] = ch3 + ch2 + ch4 + ch1
	}


//set.push("00wP")
set[set.length] = "00wp"
set.sort(reverseSort)


n=0
document.write('<img src="img/t.png"><br>')
	for(i=8;i>=1;i--){
		document.write("<img src=\"img/l.png\">");
		for(j=8;j>=1;j--){
			if (String(i) + String(j) == set[n].charAt(0)+set[n].charAt(1)){
				m=set[n]
				document.write("<img height=32 width=32 src='img/" + bw(i,j) + m.charAt(2)+m.charAt(3) + ".png'>")
				n=n+1
			}
			else{
			document.write("<img height=32 width=32 src='img/" + bw(i,j) + ".png'>")
			}
		}
		document.write("<img src=\"img/r.png\"><br>");
	}
document.write('<img src="img/u.png"><br>')
}
