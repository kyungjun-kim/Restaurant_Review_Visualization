
function renderChefInfo(chefs) {
    const chefInfo = document.getElementById('chef-info');
    chefInfo.innerHTML = `
        <img src="${chefs.image_url}" alt="${chefs.chef_name}">
        <h2>${chefs.chef_name}</h2>
    `;
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const chefId = parseInt(urlParams.get('id'));
    const chef = chefs;

    if (chef) {
        renderChefInfo(chef);
        
    } else {
        document.getElementById('chef-info').innerHTML = "<p>쉐프를 찾을 수 없습니다.</p>";
    }
});