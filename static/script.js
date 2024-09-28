// /static/script.js

document.addEventListener("DOMContentLoaded", () => {
    const startGameBtn = document.getElementById("start-game-btn");
    const resetBtn = document.getElementById("reset-btn");
    const gameStateDiv = document.getElementById("game-state");

    startGameBtn.addEventListener("click", () => {
        fetch('/start_game', { method: 'POST' })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update the game state display
                updateGameState(data);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    });

    resetBtn.addEventListener("click", () => {
        fetch('/reset', { method: 'POST' })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update the game state display
                updateGameState(data);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    });

    function updateGameState(data) {
        gameStateDiv.innerHTML = ''; // Clear the existing content
        if (data.message) {
            const messageElement = document.createElement('div');
            messageElement.className = 'message';
            messageElement.textContent = data.message;
            gameStateDiv.appendChild(messageElement);
        }
        
        if (data.players) {
            data.players.forEach(player => {
                const playerDiv = document.createElement('div');
                playerDiv.className = 'player';
                playerDiv.textContent = `${player.name}: ${player.cards.join(', ')}`;
                gameStateDiv.appendChild(playerDiv);
            });
        }
        
        if (data.lastPlayedCard) {
            const lastPlayedDiv = document.createElement('div');
            lastPlayedDiv.className = 'last-played-card';
            lastPlayedDiv.textContent = `Last Played Card: ${data.lastPlayedCard}`;
            gameStateDiv.appendChild(lastPlayedDiv);
        }
    }
});
