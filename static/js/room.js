let messagesContainer = document.getElementById("messages");
if (messagesContainer) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

const memberContainer = document.getElementById("members__container");
const memberButton = document.getElementById("members__button");

const chatContainer = document.getElementById("messages__container");
const chatButton = document.getElementById("chat__button");

let activeMemberContainer = false;

memberButton.addEventListener("click", () => {
    if (activeMemberContainer) {
        memberContainer.style.display = "none";
    } else {
        memberContainer.style.display = "block";
    }

    activeMemberContainer = !activeMemberContainer;
});

let activeChatContainer = false;

chatButton.addEventListener("click", () => {
    if (activeChatContainer) {
        chatContainer.style.display = "none";
    } else {
        chatContainer.style.display = "block";
    }

    activeChatContainer = !activeChatContainer;
});

let displayFrame = document.getElementById("stream__box");
let videoFrames = document.getElementsByClassName("video__container");
let userIdInDisplayFrame = null;

let expandVideoFrame = (e) => {
    let child = displayFrame.children[0];

    if (child) {
        document.getElementById("streams__container").appendChild(child);
    }

    displayFrame.style.display = "block";
    displayFrame.style.backgroundSize = "300px";
    displayFrame.appendChild(e.currentTarget);
    userIdInDisplayFrame = e.currentTarget.id;

    for (let i = 0; i < videoFrames.length; i++) {
        let k = videoFrames[i];
        if (k.id != userIdInDisplayFrame) {
            k.style.height = "100px";
            k.style.width = "100px";
            k.style.backgroundSize = "75px";
        }
    }
};

for (let i = 0; i < videoFrames.length; i++) {
    videoFrames[i].addEventListener("click", expandVideoFrame);
}

let hideDisplayFrame = () => {
    userIdInDisplayFrame = null;
    displayFrame.style.display = null;

    let child = displayFrame.children[0];
    document.getElementById("streams__container").appendChild(child);

    for (let i = 0; i < videoFrames.length; i++) {
        let k = videoFrames[i];
        k.style.height = "300px";
        k.style.width = "300px";
        k.style.backgroundSize = "200px";
    }
};

displayFrame.addEventListener("click", hideDisplayFrame);
