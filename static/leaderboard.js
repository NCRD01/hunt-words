
const tbody = document.getElementById("leader-body")
const dailytbody = document.getElementById("dailyleader-body")


async function leaderboard() {
    const response = await fetch("/leaderboard_data")
    const users = await response.json()

    tbody.innerHTML = "";

    users.forEach(user => {
        tbody.innerHTML += `
        <tr>
            <td>${user.username}</td>
            <td>${user.highest_score}</td>
            <td>${user.longest_streak}</td>
            <td>${user.most_words_found}</td>
        </tr>
    `;
    })
}


async function dailyleaderboard() {
    const response = await fetch("/dailyleaderboard_data")
    const users = await response.json()

    dailytbody.innerHTML = "";

    users.forEach(user => {
        dailytbody.innerHTML += `
        <tr>
            <td>${user.username}</td>
            <td>${user.highest_score}</td>
            <td>${user.longest_streak}</td>
            <td>${user.most_words_found}</td>

        </tr>
    `;
    })
}


if (tbody) {
    leaderboard();
}

if(dailytbody){
    dailyleaderboard();
}








