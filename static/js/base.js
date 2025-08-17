function toggleBalance() {
    const balanceEl = document.getElementById('wallet-balance');
    if (balanceEl.innerText.includes('****')) {
        balanceEl.innerText = balanceEl.getAttribute('data-balance');
    } else{
        balanceEl.innerText = '****';
    }
}

function copyReferral() {
    const ref = document.getElementById('referral-code');
    navigator.clipboard.writeText(ref.innerText).then(() => {
        alert("referral code copied!");
    });
}

function toggleDropdown(id) {
    document.querySelectorAll('.dropdown').forEach(d => d.classList.remove('active'));
    const selected = document.getElementById(id);
    if(!selected.classList.contains('active')){
        selected.classList.add('active');
    }
}