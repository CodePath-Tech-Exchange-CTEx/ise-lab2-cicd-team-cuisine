let mode   = 'Buy';
let choice = 'Yes';
let componentArgs = {};

function setMode(newMode) {
    mode = newMode;
    document.getElementById('buy-btn').classList.toggle('active',  mode === 'Buy');
    document.getElementById('sell-btn').classList.toggle('active', mode === 'Sell');
    const txnBtn = document.getElementById('txn-btn');
    txnBtn.style.background = mode === 'Buy' ? '#27ae60' : '#e74c3c';
}

function setChoice(newChoice) {
    choice = newChoice;
    document.getElementById('yes-btn').classList.toggle('active', choice === 'Yes');
    document.getElementById('no-btn').classList.toggle('active',  choice === 'No');
}

function validateAmount() {
    const input = document.getElementById('amount-input');
    const err   = document.getElementById('amount-error');
    const val   = parseFloat(input.value);
    const valid = !isNaN(val) && val > 0;
    err.style.display = (!input.value || valid) ? 'none' : 'block';
    return valid;
}

function submitTransaction() {
    if (!validateAmount()) {
        document.getElementById('amount-error').style.display = 'block';
        return;
    }
    const amount = parseFloat(document.getElementById('amount-input').value).toFixed(2);

    // Send data back to Streamlit
    Streamlit.setComponentValue({
        action: "submit_transaction",
        choice: choice,
        amount: amount,
        mode: mode,
    });
}

/**
 * The component's render event listener.
 * @param {Event} event The render event.
 */
function onRender(event) {
    if (!event.detail || !event.detail.args) {
        document.getElementById('bet-name').textContent = "Loading data from Python...";
        return;
    }
    
    componentArgs = event.detail.args;

    try {
        // Populate the DOM with data from Python, with fallbacks
        document.getElementById('bet-name').textContent = componentArgs.bet_name || "Unknown Bet";
        document.getElementById('rules-text').textContent = componentArgs.rules || "No rules provided.";
    
        const imageBox = document.getElementById('image-box');
        if (componentArgs.bet_image_link && componentArgs.bet_image_link !== "None") {
            imageBox.innerHTML = `<img src="${componentArgs.bet_image_link}" alt="Bet image" onerror="this.style.display='none'; this.parentElement.textContent='No Image Available';"/>`;
        } else {
            imageBox.textContent = "No Image Available";
        }
    
        document.getElementById('yes-percent-label').textContent = `Chance: ${componentArgs.yes_percent || 0}%`;
        document.getElementById('no-percent-label').textContent = `Chance: ${componentArgs.no_percent || 0}%`;
    
        document.getElementById('yes-btn').textContent = `Yes $${componentArgs.yes_value || "0.00"}`;
        document.getElementById('no-btn').textContent = `No $${componentArgs.no_value || "0.00"}`;
    
        // Set initial transaction button color
        document.getElementById('txn-btn').style.background = mode === 'Buy' ? '#27ae60' : '#e74c3c';
    } catch (err) {
        console.error("DOM population error:", err);
        document.body.innerHTML += `<div style="color:red; background:white; padding:10px; margin-top:10px; border-radius:5px;"><b>JS Error:</b> ${err.message}</div>`;
    }

    // Set a fixed iframe height to prevent the component from collapsing to 0px
    Streamlit.setFrameHeight(800);
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
// Tell Streamlit we're fully initialized and ready to start receiving render events
Streamlit.setComponentReady();
Streamlit.setFrameHeight(800);