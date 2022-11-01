// ============================================
// List of possible cards
// ============================================

let baseCards = ['goose', 'koala', 'bird', 'tiger','panda','pelican','penguin','walrus', 'flamingo', 'shark', 'horse', 'duck'];

let possibleCards = baseCards.concat(baseCards); // duplicate array items to make pairs

// ============================================
// Global Variables
// ============================================

const numCards = possibleCards.length;
const maxMatch = baseCards.length; // Maximum Pairs
let opened = [];
let numStars = 3;
let numMatch = 0;
let numMoves = 0;
let turns = 0;
let pairs_found = 0;
let is_match = false;
let hint_cards = []

// Timers 
let seconds = 0;
let minutes = 0;
let t;


const showStar = ['<li><i class="fa fa-star"></i></li><li><i class="fa fa-star-o"></i></li><li><i class="fa fa-star-o"></i></li>',  // 1 star
                  '<li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li><li><i class="fa fa-star-o"></i></li>',  // 2 stars
                  '<li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li>' // 3 stars
                 ];


// ============================================
// Send data to flask
// ============================================
function sendFlask(flag, data){
  fetch('http://192.168.1.61:5000/', {
        headers : {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
          [flag]: data
        })
    })
    .then(function (response){

        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log("response is:" , response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })
    .catch(function(error) {
        console.log(error);
    });  
}

function checkFirstVisit() {
  if(document.cookie.indexOf('mycookie')==-1) {
    // cookie doesn't exist, create it now
    document.cookie = 'mycookie=1';
  }
}


// ============================================
// Shuffle
// source: http://stackoverflow.com/a/2450976
// ============================================

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;

    while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;
        temporaryValue = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temporaryValue;
    }
  
    return array;
}

// ============================================
// Init the Game
// Clear deck, init variables, shuffle cards and put them back on
// ============================================

// color the card suggested by robot
function hintReceivedByRobot(){
    // sending a connect request to the server.
    socket = io.connect('http://192.168.56.1:5000/');
  
    socket.on('robot_hint', function(msg) {
      hint_cards = msg.data
      if(hint_cards.length > 0){
        document.querySelectorAll(".card").forEach((card) => { 
          if(hint_cards.includes(Number(card.id)))
            card.classList.add('hint');
        });
      }
    });
}

function initGame() {
    document.querySelector('.overlay').style.display = 'none';
    document.querySelector('.deck').innerHTML = '';
    var array = shuffle(possibleCards);
    sendFlask("matrix", array);

    opened = []; 
    numStars = 3;
    numMoves = 0;
    numMatch = 0;
    face_up_cards = 0;
    turns = 0;
    pairs_found = 0;
    is_match = false;

    resetTimer();
    runTimer();
    printStars();
    printMoves();

    for(i=0;i<numCards;i++) {
        document.querySelector('.deck').innerHTML += `<li class="card", id = "`+(i)+`" ><img src="/static/images/${possibleCards[i]}.svg"/></li>`;
    };
  
  

    // ============================================
    // Set up event listener
    // 1. Click a card,  if it's already shown, quit function
    // 2. If it's not shown, show the card, add it to opened array. 
    // 3. If there's already an item in the opened array, check if it's match. 
    // 4. run match or unmatch function, clear opened array for the next match check.
    // 5. Calculate the stars for each move.
    // 6. If reach maximum pairs, end the game, show congrats message
    // ============================================

    document.querySelectorAll(".card").forEach((card) => {  
        card.addEventListener("click", function () {

            // remove hint cause card has been clicked
            card.classList.remove('hint')

            if (card.classList.contains('show')){
                return; // exit function if the card is already opened.
            }

            card.classList.add('show','animated','flipInY');

            let currentCard = card.innerHTML;
            opened.push(currentCard);

            // get name of image without path and format
            var filename = currentCard.replace(/^.*[\\\/]/, '')
            var clicked_card_name = filename.replace(/\..+$/, '');

            // get card position
            var positionCard = Number(this.id);
            var index_row = Math.floor(positionCard/6)
            var index_col = positionCard % 6
            
            // create coordinates of the clicked card
            clicked_card_position = [];
            clicked_card_position.push(index_row, index_col);

        
            face_up_cards = 1;

            if(opened.length > 1) {
                face_up_cards = 2;
            
                if(currentCard === opened[0]) {
                    match();
                    pairs_found ++;
                    sendFlask("data",
                        {
                            "clicked_card_name": clicked_card_name,
                            "clicked_card_position": clicked_card_position,
                            "n_face_up": face_up_cards,
                            "match": [
                            true,
                            numMatch
                            ]
                        }
                    )
                } else {
                    unmatch();
                    sendFlask("data",
                        {
                            "clicked_card_name": clicked_card_name,
                            "clicked_card_position": clicked_card_position,
                            "n_face_up": face_up_cards,
                            "match": [
                                false,
                                0
                            ]
                        }
                    )
                }
            } else {
                sendFlask("data",
                    {
                        "clicked_card_name": clicked_card_name,
                        "clicked_card_position": clicked_card_position,
                        "n_face_up": face_up_cards,
                        "match": [
                            false,
                            0
                        ]
                    }
                )
                is_match = false;
            }
        
            starCount(); 
            printMoves();

            if(numMatch === maxMatch ) {
                stopTimer();
                congrats();
            }

            turns++;

            sendFlask("game", {
                "open_card_name": clicked_card_name,
                "open_card_position": clicked_card_position,
                "pairs": pairs_found,
                "turn": turns,
                "match": is_match
            });
        })
    });
};

initGame();

// ============================================
// Match + Unmatch function
// ============================================


function match() {
    numMoves++;
    numMatch++;
    is_match = true
    opened = [];

    document.querySelectorAll(".show").forEach((matchedCard) => {
        matchedCard.classList.add('match','animated','flip')
        matchedCard.classList.remove('show')
    });
};


function unmatch() {
    numMoves++;
    is_match = false;
    opened = [];

    document.querySelectorAll(".show:not(.match)").forEach((unmatchedCard) => {
        unmatchedCard.classList = 'card show unmatch animated shake';
        document.querySelectorAll('.unmatch').forEach((unmatchedCard) => {
        setTimeout(function() {
            unmatchedCard.classList = 'animated flipInY card';
        }, 600);
        })
    });
};




// ============================================
// Calculate Stars by the moves and print it
// ============================================

function starCount() {

    if(numMoves < 34) {
        numStars = 3;
    } else if (numMoves < 40) {
        numStars = 2;
    } else {
        numStars = 1;
    };

    printStars();
};


// print "stars", "moves", "matches" to the page
function printStars() {
  document.querySelectorAll('.stars').forEach(panel => panel.innerHTML = showStar[numStars-1])
}


function printMoves(){
  document.querySelectorAll('.moves').forEach(move => move.textContent = numMoves)
}


// ============================================
// Timer
// ref: https://jsfiddle.net/Daniel_Hug/pvk6p/
// ============================================


function twoDigits(number) {
       return (number < 10 ? '0' : '') + number;
}


function timer() {
    seconds++;
    if (seconds >= 60) {
        seconds = 0;
        minutes++;
    }
  
    updateTimer()
    runTimer();
}


function runTimer() {
  t = setTimeout(timer, 1000);
}

function resetTimer() {
    stopTimer();
    seconds = 0; minutes = 0;
    updateTimer()
}

function updateTimer(){
    document.querySelectorAll(".timer-seconds").forEach(item=> item.textContent = twoDigits(seconds));
    document.querySelectorAll(".timer-minutes").forEach(item=> item.textContent = twoDigits(minutes));
}

function stopTimer() {
  clearTimeout(t);
}


// ============================================
// Restart
// ============================================

document.querySelectorAll('.restart').forEach(item=>
    item.addEventListener("click", function(){
        //sendFlask("True", "refreshed");
        initGame();
    })
);

// ============================================
// Congrats Message
// ============================================

const finishImg = ['walrus', 'penguin','tiger'];
const finishMsg = ['Oh man... even a walrus can do better','Good job, pal! Well done','Geez, That\'s amazing!'];


function congrats() {
    stopTimer();
    setTimeout(function(){
        // switch messages and images base on number of stars
        document.querySelector('.switch-msg').innerHTML = 
        `
            <h2>${finishMsg[numStars-1]}</h2>
            <img src="/static/images/${finishImg[numStars-1]}.svg" alt="" width="300">
        `
        document.querySelector('.overlay-content').classList.add('animated','bounceIn')
    }, 100);

    setTimeout(function(){
        document.querySelector('.overlay').style.display = 'block'
    }, 300);

    var results = {
        "moves": numMoves,
        "minutes": minutes,
        "seconds": seconds
    };
};
