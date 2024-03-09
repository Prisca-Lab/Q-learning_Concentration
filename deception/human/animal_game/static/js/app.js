// List of possible cards
const baseCards = ['goose', 'koala', 'bird', 'tiger', 'panda', 'pelican', 'penguin', 'walrus', 'flamingo', 'shark', 'horse', 'duck'];
const possibleCards = baseCards.concat(baseCards); // Duplicate array items to make pairs

// Global Variables
const numCards = possibleCards.length;
const maxMatch = baseCards.length;      // Maximum Pairs
let opened = [];
let numStars = 3;
let numMatch = 0;
let numMoves = 0;
let turns = 0;
let isMatch = false;
let hintCards = [];
let timeHint = 3500;
let speechFinished = false;

// For communication with Server
let id_player = -1
let isMultithreading = false;
const url = ''
let socket_address = ''
let language = 'ita'

// Timers 
let seconds = 0;
let minutes = 0;
let t;

let myMinutes = 0;
let mySeconds = 0;
let myT;



const showStar = [
    '<li><i class="fa fa-star"></i></li><li><i class="fa fa-star-o"></i></li><li><i class="fa fa-star-o"></i></li>', // 1 star
    '<li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li><li><i class="fa fa-star-o"></i></li>', // 2 stars
    '<li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li><li><i class="fa fa-star"></i></li>' // 3 stars
];

// If game is not finished and user try to refresh the page
window.addEventListener('beforeunload', function (e) {
    if (!(numMatch == 12)) {
        var confirmationMessage = 'Sei sicuro di voler aggiornare la pagina? Il gioco non è ancora finito.';

        (e || window.event).returnValue = confirmationMessage;
        return confirmationMessage;
    }
});

// Send data to Flask server
function sendFlask(flag, data, route){
  //alert("route is" + route + "while id is" + id_player)
  fetch(route + "/" + id_player, {
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

// Check if it's the first visit
function checkFirstVisit() {
    if (document.cookie.indexOf('mycookie') === -1) {
        document.cookie = 'mycookie=1';
    } else {
        sendFlask("refreshed", "True", "/");
    }
}

// Shuffle array
function shuffle(array) {
    return array.sort(() => Math.random() - 0.5);
}

// Initialize the Game
function initGame() {
    document.querySelector('.overlay').style.display = 'none';
    document.querySelector('.deck').innerHTML = '';

    const shuffledCards = shuffle(possibleCards);
    // send to flask game board
    sendFlask("matrix", shuffledCards, '/game_board');

    opened = [];
    numStars = 3;
    numMoves = 0;
    numMatch = 0;
    turns = 0;
    isMatch = false;

    resetTimer();
    runTimer();
    myResetTimer();
    myRunTimer();
    printStars();
    printMoves();

    shuffledCards.forEach((card, index) => {
        const cardElement = document.createElement('li');
        cardElement.classList.add('card');
        cardElement.id = index;
        cardElement.innerHTML = `<img src="/static/images/${card}.svg"/>`;
        cardElement.addEventListener('click', () => cardClickListener(cardElement, card));
        document.querySelector('.deck').appendChild(cardElement);
    });
}

// Handle card clicks
function cardClickListener(cardElement, card) {
    // if pair is already found the card of pair can't be clicked
    if (cardElement.classList.contains('match')) {
        return;
    }

    setTimeout(() => {
        document.querySelectorAll(".card").forEach(card => {
            card.classList.remove('hint');
            card.classList.remove('flipInY');
            document.querySelector('.message-bubble').style.display = 'none';
        });

        if (cardElement.classList.contains('show')) {
            return;
        }

        cardElement.classList.add('show', 'animated', 'flipInY');
        opened.push(card);

        const filename = card.replace(/^.*[\\\/]/, '');
        const clickedCardName = filename.replace(/\..+$/, '');

        const positionCard = Number(cardElement.id);
        const indexRow = Math.floor(positionCard / 6);
        const indexCol = positionCard % 6;

        const clickedCardPosition = [indexRow, indexCol];

        if (opened.length > 1) {
            if (card === opened[0]) {
                match();
            } else {
                unmatch();
            }
        } else {
            isMatch = false;
        }

        starCount();
        printMoves();

        if(numMatch === maxMatch ) {
            stopTimer();
            congrats();
        }

        // update turns number
        turns++;

        sendFlask("game", {
            "open_card_name": clickedCardName,
            "position": clickedCardPosition,
            "pairs": numMatch,
            "turn": turns,
            "match": isMatch,
            "n_face_up": opened.length,
            "time_until_match": `${myMinutes}:${mySeconds}`,
            "time_game": `${minutes}:${seconds}`
        }, "/player_move");

        if (isMatch) {
            myMinutes = 0;
            mySeconds = 0;
        }

        
    }, 0);
}

// Match function
function match() {
    numMoves++;
    numMatch++;
    isMatch = true;
    opened = [];

    document.querySelectorAll(".show").forEach(matchedCard => {
        matchedCard.classList.add('match', 'animated', 'flip');
        matchedCard.classList.remove('show');
    });
}

// Unmatch function
function unmatch() {
    numMoves++;
    isMatch = false;
    opened = [];

    document.querySelectorAll(".show:not(.match)").forEach(unmatchedCard => {
        unmatchedCard.classList = 'card show unmatch animated shake';
        document.querySelectorAll('.unmatch').forEach(unmatchedCard => {
            setTimeout(() => {
                unmatchedCard.classList = 'animated flipInY card';
            }, 600);
        });
    });
}

// Calculate Stars by the moves and print it
function starCount() {
    if (numMoves < 25) {
        numStars = 3;
    } else if (numMoves < 30) {
        numStars = 2;
    } else {
        numStars = 1;
    }
    printStars();
}

// Print "stars", "moves", "matches" to the page
function printStars() {
    document.querySelectorAll('.stars').forEach(panel => panel.innerHTML = showStar[numStars - 1]);
}

function printMoves() {
    document.querySelectorAll('.moves').forEach(move => move.textContent = numMoves);
}

// Timer functions
function twoDigits(number) {
    return (number < 10 ? '0' : '') + number;
}

function myTimer() {
    mySeconds++
    if (mySeconds >= 60) {
        mySeconds = 0;
        myMinutes++;
    }
    myRunTimer();
}

function myRunTimer() {
    myT = setTimeout(myTimer, 1000);
}

function timer() {
    seconds++;
    if (seconds >= 60) {
        seconds = 0;
        minutes++;
    }

    updateTimer();
    runTimer();
}

function runTimer() {
    t = setTimeout(timer, 1000);
}

function resetTimer() {
    stopTimer();
    seconds = 0;
    minutes = 0;
    updateTimer();
}

function myResetTimer() {
    myStopTimer();
    mySeconds = 0;
    myMinutes = 0;
}

function updateTimer() {
    document.querySelectorAll(".timer-seconds").forEach(item => item.textContent = twoDigits(seconds));
    document.querySelectorAll(".timer-minutes").forEach(item => item.textContent = twoDigits(minutes));
}

function stopTimer() {
    clearTimeout(t);
}

function myStopTimer() {
    clearTimeout(myT)
}

// Restart function
document.querySelectorAll('.restart').forEach(item =>
    item.addEventListener("click", function () {
        id_player = -1
        console.log("Before reshing id is", id_player)
        fetch('/get_file_config/' + id_player)
            .then(response => response.json())
            .then(data => {
                id_player = data.id
                socket_address = 'robot_hint_' + id_player
                console.log("After refresh id is:", id_player, "and socket addr: ", socket_address)
                hintReceivedByRobot(socket_address)
                setTimeout(initGame, 500);
                })
            .catch(error => console.error('Error:', error));
    })
);

// Congrats Message
const finishImg = ['walrus', 'penguin', 'tiger'];
const finishMsg = ['Oh man... even a walrus can do better', 'Good job, pal! Well done', 'Geez, That\'s amazing!'];

// Handle robot suggestions
function hintReceivedByRobot(socket_address) {
    const socket = io.connect(url);

    console.log("socket addr", socket_address)
    socket.on('Speech', handleSpeechEvent);
    socket.on(socket_address, handleRobotHintEvent);
    
    // Once the robot has finished uttering the suggestion, remove the pop-up 
    function handleSpeechEvent(msg) {
        speechFinished = true;
        hidePopup();
    }

    // Highlight (in red) the location of the card (or the row/column) suggested by the robot
    function handleRobotHintEvent(msg) {
        const obj = JSON.parse(msg);
        const isRobotConnected = obj.action.isRobotConnected;

        if (isRobotConnected != false) {
            lookRobotPopup();
        } else {
            timeHint = 0;
        }

        setTimeout(applyHint, timeHint);

        function applyHint() {
            const suggestion = obj.action.suggestion;
            const row = obj.action.position[0] - 1
            const col = obj.action.position[1] - 1

            // Show message near to robot icon if app is multithread
            if(isMultithreading == true){
                document.querySelector('.message-bubble').style.display = 'block';
                // get msg
                const messageBubbleElement = document.querySelector('.message-bubble');
                // create text based on hint received
                let textHint = ''
                if(suggestion == "row") 
                    textHint = 'Prova la riga ' + (row + 1)
                else if(suggestion == "column")
                    textHint = 'Prova la colonna ' + (col + 1)
                else
                    textHint = 'Prova in riga ' + (row + 1) + ' e colonna ' + (col + 1)
                // show msg
                messageBubbleElement.textContent = textHint;
            }

            document.querySelectorAll(".card").forEach((card) => {
                if(card.classList.contains("flipInY") == true) //&& (turns + 1) % 2 != 0)
                    card.classList.remove('flipInY')

                if(card.classList.contains("match") == false && card.classList.contains("flipInY") == false 
                                                             && card.classList.contains("show") == false){
                    if(suggestion == "row"){
                        if(row == Math.floor(card.id/6))
                            card.classList.add('hint');
                    }

                    if(suggestion == "column"){
                        if(col == card.id % 6)
                            card.classList.add('hint');
                        }
                    }

                    if(suggestion == "card"){
                        if(row == Math.floor(card.id/6) && (col == card.id % 6))
                            card.classList.add('hint');
                    }
            });
        }
    }
}

// Pop-up when the robot provide a suggestion
function lookRobotPopup() {
    stopTimer();
    myStopTimer();

    if(language == 'en'){
        // get sentence of pop-up
        var suggestionHeading = document.querySelector('.suggestion-content h2');
        // set in english
        suggestionHeading.textContent = 'Hey, the robot is about to say something!';
    }

    document.querySelector('.msg').innerHTML =
        `
            <img src="/static/images/robot.svg" alt="" width="250">
        `
    document.querySelector('.suggestion-content').classList.add('animated', 'bounceIn')

    setTimeout(() => {
        document.querySelector('.suggestion').style.display = 'block'
    }, 10);
}

// hide pop-up when robot has finished to speak
function hidePopup() {
    stopTimer();
    myStopTimer();

    setTimeout(() => {
        document.querySelector('.suggestion').style.display = 'block'
    }, 10);

    runTimer();
    myRunTimer();

    setTimeout(() => {
        document.querySelector(".suggestion").style.display = "none";
    }, 500)
}

function congrats() {
    stopTimer();
    setTimeout(() => {
        document.querySelector('.switch-msg').innerHTML =
            `
            <h2>${finishMsg[numStars - 1]}</h2>
            <img src="/static/images/${finishImg[numStars - 1]}.svg" alt="" width="300">
        `
        document.querySelector('.overlay-content').classList.add('animated', 'bounceIn')
    }, 100);

    setTimeout(() => {
        document.querySelector('.overlay').style.display = 'block'
    }, 300);
};


/**
 * Start the game.
 * If the JSON data is false, the game will start immediately without requiring the 'Play' button to be clicked, 
 * otherwise, it will display a pop-up, prompting the user to click 'Play' to start the game.
 */
document.addEventListener('DOMContentLoaded', function() {
    if(isMultithreading == false)
        id_player = -1

    fetch('/get_file_config/' + id_player)
        .then(response => response.json())
        .then(data => {
            console.log("msg", data);
            
            isMultithreading = data.multithreading
            // show icon of robot if app is multithreading
            const robotIcon = document.getElementById('robot-image');
            if(isMultithreading == true){
                robotIcon.style.display = 'block'; // show robot icon
            } else {
                robotIcon.style.display = 'none'; 
            }

            language = data.language

            // init game showing pop-up based on config setting
            if(data.message == false) {
                console.log("data is false");
                console.log("player id is", data.id)
                id_player = data.id
                socket_address = 'robot_hint_' + id_player
                console.log("init address", socket_address)
                hintReceivedByRobot(socket_address)
                initGame();
            } else {
                console.log("data true");
                id_player = data.id
                socket_address = 'robot_hint_' + id_player
                console.log("init address", socket_address)
                hintReceivedByRobot(socket_address)
                showPopup();
            }
        })
        .catch(error => console.error('Error:', error));
});

function showPopup() {
    stopTimer();
    setTimeout(() => {
        document.querySelector('.start-msg').innerHTML =
            `
            <h1>Matching Game</h1>
            <img src="/static/images/pelican.svg" alt="" width="200">
            `;
        document.querySelector('.overlay-content-start').classList.add('animated', 'bounceIn');
    }, 100);

    setTimeout(() => {
        document.querySelector('.overlay-start').style.display = 'block';
    }, 300);

    document.querySelector('.start').addEventListener('click', function() {
        document.querySelector('.overlay-start').style.display = 'none';
        initGame();
    });
}
