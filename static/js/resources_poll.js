/**
 * Polls /api/hospitals/<id>/resources/ every 8s and updates the detail page panel.
 */
(function () {
  var panel = document.getElementById("resources-panel");
  if (!panel) return;
  var url = panel.getAttribute("data-poll-url");
  if (!url) return;

  function apply(data) {
    var icu = panel.querySelector('[data-res="icu_avail"]');
    var gen = panel.querySelector('[data-res="gen_avail"]');
    var vent = panel.querySelector('[data-res="vent"]');
    var amb = panel.querySelector('[data-res="amb"]');
    var upd = panel.querySelector('[data-res="updated"]');
    if (icu) icu.textContent = data.icu_beds_available;
    if (gen) gen.textContent = data.general_beds_available;
    if (vent) vent.textContent = data.ventilators_available;
    if (amb) amb.textContent = data.ambulances_available;
    if (upd && data.updated_at) upd.textContent = "Last update: " + data.updated_at;
  }

  function tick() {
    fetch(url, { credentials: "same-origin" })
      .then(function (r) {
        return r.json();
      })
      .then(apply)
      .catch(function () {});
  }

  setInterval(tick, 8000);
})();
