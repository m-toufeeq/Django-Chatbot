var data = {
    chatinit: {
        title: ["Hi there<span class='emoji'> &#128075;</span>", "I see you've logged the symptom of acne today. I’ll ask a few questions to help understand your situation. Ready?"],
        options: ["Yes <span class='emoji'> &#128250;</span>", "No <span class='emoji'> &#127925;</span>"]
    },
    yes: {
        title: ["I understand you're experiencing acne. I'll ask you a few questions to better understand your situation and provide some suggestions. Ready?"],
        options: ['Proceed']
    },
    proceed: {
        title: ["On a scale from 1 to 10, how severe is your acne right now? (1 being mild and 10 being very severe)"],
        options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    },
    severity_low: {
        title: ["Thanks for the info! How long have you been experiencing acne?"],
        options: ["Few days", "A week", "Month"]
    },
    duration: {
        title: ["Where is your acne primarily located?"],
        options: ["Face", "Back", "Shoulders"]
    },
    symptoms: {
        title: ["Do you have any other symptoms accompanying the acne?"],
        options: ["Itching", "Redness", "Swelling", "No other symptoms"]
    },
    diet: {
        title: ["Have you recently made any changes to your diet, skincare routine, or started any new medications?"],
        options: ["Sure", "Nope"]
    },
    stresslevels: {
        title: ["How would you describe your stress levels lately?"],
        options: ["High", "Moderate", "Low"]
    },
    final: {
        title: ["Thank you for providing this information. Based on what you’ve shared, I'll provide some recommendations. See below:"],
        options: ["See Recommendations"]
    },
    recommendations: {
        title: ["Here are some suggestions to help manage your acne:",
                "If severity is high and duration is long: Consider seeing a dermatologist for a professional evaluation. In the meantime, keep your skin clean and avoid touching your face frequently.",
                "If associated symptoms are severe: Try to avoid using harsh skincare products. Look for products specifically designed for acne-prone skin.",
                "If recent changes in diet or routine: Review recent changes and see if they might be contributing to your acne. A balanced diet and consistent skincare routine can help."
               ],
        options: ["Go ahead"]
    },
    reminder: {
        title: ["Would you like to set a reminder to track your acne progress or get more tips on managing acne?"],
        options: ["Absolutely", "I decline"]
    },
    close: {
        title: ["Would you like to set a reminder to track your acne progress or get more tips on managing acne?"],
        options: ["That would be wonderful", "Later"]
    },
    ending: {
        title: ["Great! I'll set a reminder for you",  "Alright! If you need any more assistance or have other symptoms to discuss, feel free to reach out."],
        options: []
    }
    
};
console.log(data);

document.getElementById("init").addEventListener("click", showChatBot);
var cbot = document.getElementById("chat-box");

var len1 = data.chatinit.title.length;

function showChatBot() {
    if (this.innerText == 'START CHAT') {
        document.getElementById('test').style.display = 'block';
        document.getElementById('init').innerText = 'CLOSE CHAT';
        initChat();
    } else {
        location.reload();
    }
}

function initChat() {
    j = 0;
    cbot.innerHTML = '';
    for (var i = 0; i < len1; i++) {
        setTimeout(handleChat, (i * 500));
    }
    setTimeout(function () {
        showOptions(data.chatinit.options);
    }, ((len1 + 1) * 500));
}

var j = 0;

function handleChat() {
    var elm = document.createElement("p");
    elm.innerHTML = data.chatinit.title[j];
    elm.setAttribute("class", "msg");
    cbot.appendChild(elm);
    j++;
    handleScroll();
}

function showOptions(options) {
    for (var i = 0; i < options.length; i++) {
        var opt = document.createElement("span");
        var inp = '<div>' + options[i] + '</div>';
        opt.innerHTML = inp;
        opt.setAttribute("class", "opt");
        opt.addEventListener("click", handleOpt);
        cbot.appendChild(opt);
        handleScroll();
    }
}

function handleOpt() {
    var str = this.innerText;
    var textArr = str.split(" ");
    var findText = textArr[0].toLowerCase();

    console.log("User selected:", findText); // Log the selected option
    
    document.querySelectorAll(".opt").forEach(el => {
        el.remove();
    });

    var elm = document.createElement("p");
    elm.setAttribute("class", "test");
    elm.innerHTML = '<span class="rep">' + this.innerText + '</span>';
    cbot.appendChild(elm);

    routeBasedOnResponse(findText);
}
function routeBasedOnResponse(findText) {
    console.log("Routing based on:", findText); // Log the branching
    
    if (findText === "yes") {
        handleResults(data.yes.title, data.yes.options);
    } 
    else if (findText === "proceed") {
        handleResults(data.proceed.title, data.proceed.options);
    } 
    else if (["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"].includes(findText)) {
        handleResults(data.severity_low.title, data.severity_low.options);
    } 
    else if (["few", "a", "month"].includes(findText)) {
        handleResults(data.duration.title, data.duration.options);
    }
    else if (["face", "back", "shoulders"].includes(findText)) {
        handleResults(data.symptoms.title, data.symptoms.options);
    } 
    else if (["itching", "redness", "swelling", "no"].includes(findText)) {
        handleResults(data.diet.title, data.diet.options);
    } 
    else if (["sure", "nope"].includes(findText)) {
        handleResults(data.stresslevels.title, data.stresslevels.options);
    } 
    else if (["high", "moderate", "low"].includes(findText)) {
        handleResults(data.final.title, data.final.options);
    } 
    else if (["see"].includes(findText)) {
        handleResults(data.recommendations.title, data.recommendations.options);
    } 
    else if (["go"].includes(findText)) {
        handleResults(data.reminder.title, data.reminder.options);
    }
    else if (["absolutely", "i"].includes(findText)) {  
        handleResults(data.close.title, data.close.options);
    }
    else if (["that", "later"].includes(findText)) {
        handleResults(data.ending.title, data.ending.options);
    }
}

function handleDelay(title) {
    var elm = document.createElement("p");
    elm.innerHTML = title;
    elm.setAttribute("class", "msg");
    cbot.appendChild(elm);
}

function handleResults(title, options) {
    for (let i = 0; i < title.length; i++) {
        setTimeout(function () {
            handleDelay(title[i]);
        }, i * 500);
    }

    setTimeout(function () {
        showOptions(options);
    }, title.length * 500);
}

function handleScroll() {
    var elem = document.getElementById('chat-box');
    elem.scrollTop = elem.scrollHeight;
}
