const express = require('express');
const sqrl = require('squirrelly');
const app = express();
const XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;

var currentDeck = "";
var template = `<h1>Legends of Runeterra Deck Generator</h1>
<button id="btn" type="button">Generate New Deck</button>
<p>
<div id="deck">
    Test
</div>
</p>
<script>
document.getElementById("btn").addEventListener("click", function(e) {
    generateDeck();
});
</script>
`;
var data = {
    deck: currentDeck,
    func: generateDeck()
};

function generateDeck() {
    console.log("Button Clicked");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 & this.status == 200) {
            document.getElementById("deck").innerHTML = currentDeck;
        }
    };
    xhttp.open("GET", "ajax_info.txt", true);
    xhttp.send();/*
    var spawn = require("child_process").spawn;
    var process = spawn('python', ["./DeckAlgo.py"]);
    process.stdout.on('data', function (deck) {
        currentDeck = deck;
    });
*/
}

var result = sqrl.Render(template, data);

app.set('view engine', 'squirrelly');

app.get('/', function (req, res) {
    res.send(result);
});

app.listen(3000, function () {
    console.log("App listening on port 3000.")
});
