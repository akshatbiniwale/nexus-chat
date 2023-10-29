let handleMemberJoined = async (memberId) => {
    console.log("New member has joined!", memberId);
    addMemberToDOM(memberId);

    let members = await channel.getMembers();
    updateMemberTotal(members);

    let { name } = await rtmClient.getUserAttributesByKeys(memberId, ["name"]);
    addBotMessageToDOM(`Welcome to the room ${name}! 👋`);
};

let addMemberToDOM = async (memberId) => {
    let { name } = await rtmClient.getUserAttributesByKeys(memberId, ["name"]);

    let membersWrapper = document.getElementById("member__list");
    let memberItem = `<div class="member__wrapper" id="member__${memberId}__wrapper">
                        <span class="green__icon"></span>
                        <p class="member_name">${name}</p>
                    </div>`;

    membersWrapper.insertAdjacentHTML("beforeend", memberItem);
};

let updateMemberTotal = async (members) => {
    let total = document.getElementById("members__count");
    total.innerText = members.length;
    let totalOnline = document.getElementById("rooms__count");
    totalOnline.innerText = members.length;
};

let handleMemberLeft = async (memberId) => {
    removeMemberFromDOM(memberId);

    let members = await channel.getMembers();
    updateMemberTotal(members);
};

let removeMemberFromDOM = async (memberId) => {
    let membersWrapper = document.getElementById(
        `member__${memberId}__wrapper`
    );
    let name =
        membersWrapper.getElementsByClassName("member_name")[0].textContent;
    membersWrapper.remove();

    addBotMessageToDOM(`${name} has left the room.`);
};

let getMembers = async () => {
    let members = await channel.getMembers();
    updateMemberTotal(members);

    for (let i = 0; members.length > i; i++) {
        addMemberToDOM(members[i]);
    }
};

let handleChannelMessage = async (messageData, memberId) => {
    let data = JSON.parse(messageData.text);

    if (data.type === "chat") {
        addMessageToDOM(data.displayName, data.message);
    }

    if (data.type === "user_left") {
        document.getElementById(`user-container-${data.uid}`).remove();

        if (userIdInDisplayFrame === `user-container-${uid}`) {
            displayFrame.style.display = null;

            for (let i = 0; i < videoFrames.length; i++) {
                let k = videoFrames[i];
                k.style.height = "300px";
                k.style.width = "300px";
                k.style.backgroundSize = "200px";
            }
        }
    }
};

let sendMessage = async (e) => {
    e.preventDefault();

    let message = e.target.message.value;
    channel.sendMessage({
        text: JSON.stringify({
            type: "chat",
            message: message,
            displayName: displayName,
        }),
    });

    addMessageToDOM(displayName, message);

    e.target.reset();
};

let addMessageToDOM = async (name, message) => {
    let messagesWrapper = document.getElementById("messages");

    let newMessage = `<div class="message__wrapper">
                        <div class="message__body">
                            <strong class="message__author">${name}</strong>
                            <p class="message__text">${message}</p>
                        </div>
                    </div>`;

    messagesWrapper.insertAdjacentHTML("beforeend", newMessage);

    let lastMessage = document.querySelector(
        "#messages .message__wrapper:last-child"
    );

    if (lastMessage) {
        lastMessage.scrollIntoView();
    }
};

let addBotMessageToDOM = async (botMessage) => {
    let messagesWrapper = document.getElementById("messages");

    let newMessage = `<div class="message__wrapper">
                        <div class="message__body__bot">
                            <strong class="message__author__bot">🤖 connect+ Bot</strong>
                            <p class="message__text__bot">${botMessage}</p>
                        </div>
                    </div>`;

    messagesWrapper.insertAdjacentHTML("beforeend", newMessage);

    let lastMessage = document.querySelector(
        "#messages .message__wrapper:last-child"
    );

    if (lastMessage) {
        lastMessage.scrollIntoView();
    }
};

let leaveChannel = async () => {
    await channel.leave();
    await rtmClient.logout();
};

window.addEventListener("beforeunload", leaveChannel);
let messageForm = document.getElementById("message__form");
messageForm.addEventListener("submit", sendMessage);

console.log(document.getElementById("rooms__count"));
