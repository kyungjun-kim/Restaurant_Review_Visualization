
function renderChefInfo(chefs) {
    const chefInfo = document.getElementById('chef-info');
    chefInfo.innerHTML = `
        <img src="${chefs.image_url}" alt="${chefs.chef_name}">
        <h2>${chefs.chef_name}</h2>
    `;
}

function generateWordcloud(words) {
    const width = document.getElementById('wordcloud').offsetWidth;
    const height = 400;

    const layout = d3.layout.cloud()
        .size([width, height])
        .words(words.map(d => ({ text: d.text, size: 10 + d.value * 90 })))
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .font("Impact")
        .fontSize(d => d.size)
        .on("end", draw);

    layout.start();

    function draw(words) {
        d3.select("#wordcloud").append("svg")
            .attr("width", layout.size()[0])
            .attr("height", layout.size()[1])
            .append("g")
            .attr("transform", `translate(${layout.size()[0] / 2},${layout.size()[1] / 2})`)
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("font-family", "Impact")
            .style("fill", () => d3.schemeCategory10[~~(Math.random() * 10)])
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${[d.x, d.y]})rotate(${d.rotate})`)
            .text(d => d.text);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const chefId = parseInt(urlParams.get('id'));
    const chef = chefs;

    if (chef) {
        renderChefInfo(chef);
        // 여기에서 실제 리뷰 데이터
        const words = [
            { text: "맛있다", value: parseFloat(Math.random().toFixed(1)) },
            { text: "분위기", value: parseFloat(Math.random().toFixed(1)) },
            { text: "서비스", value: parseFloat(Math.random().toFixed(1)) },
            { text: "친절", value: parseFloat(Math.random().toFixed(1)) },
            { text: "EVEN함", value: parseFloat(Math.random().toFixed(1)) },
            { text: "익힘정도", value: parseFloat(Math.random().toFixed(1)) },
            { text: "파인다이닝", value: parseFloat(Math.random().toFixed(1)) },
            { text: "생존", value: parseFloat(Math.random().toFixed(1)) },
            // ... 더 많은 단어 데이터
        ];
        generateWordcloud(words);
    } else {
        document.getElementById('chef-info').innerHTML = "<p>쉐프를 찾을 수 없습니다.</p>";
    }
});