let mode   = 'Buy';
let choice = 'Yes';

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
    showToast(`✅ Transaction Successful! ${mode} ${choice} — $${amount}`);
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.display = 'block';
    // Reset animation
    toast.style.animation = 'none';
    toast.offsetHeight; // reflow
    toast.style.animation = 'fadeInOut 3s ease forwards';
    setTimeout(() => { toast.style.display = 'none'; }, 3000);
}

// Set initial transaction button color
document.getElementById('txn-btn').style.background = '#27ae60';