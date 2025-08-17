function toggleWallet() {
    const balance = document.getElementById('wallet-balance');
    balance.classList.toggle('blur-sm');
}

function copyReferral() {
    const input = document.getElementById('referral-code');
    input.Select();
    input.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(input.value)
    alert('Referral link copied!');
}

function toggleDrop(id) {
    document.querySelectorAll('[id^="' + id.split('-')[0] + '-"]').forEach(el => {
        if (el.id===id) {
            el.classList.toggle('hidden');
        } else{
            el.classList.add('hidden');
        }
    })
}
