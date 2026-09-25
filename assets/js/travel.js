"use strict";
(() => {
  const dataNode = document.getElementById("travel-data");
  if (!dataNode) return;
  const { photos, countries = [] } = JSON.parse(dataNode.textContent);
  const indexEntries = new Map(countries.flatMap(country => [country, ...country.cities.map(city => ({ ...city, name: `${city.name}, ${country.name}` }))]).map(entry => [entry.id, entry]));
  const cards = new Map([...document.querySelectorAll(".travel-photo")].map(card => [card.dataset.photoId, card]));
  const placeButtons = [...document.querySelectorAll(".travel-place")];
  const radius = document.getElementById("travel-radius");
  const selection = document.getElementById("travel-selection");
  const count = document.getElementById("travel-count");
  const status = document.getElementById("travel-map-status");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let visible = photos;
  let anchor = null;
  let map, markers, radiusCircle;

  function showPhotos(items, title, activePlace = null) {
    visible = items;
    const ids = new Set(items.map(photo => photo.id));
    cards.forEach((card, id) => { card.hidden = !ids.has(id); });
    selection.textContent = title;
    count.textContent = `${items.length} photograph${items.length === 1 ? "" : "s"}`;
    document.getElementById("travel-empty").hidden = items.length > 0;
    radius.disabled = !anchor || !map;
    placeButtons.forEach(button => {
      const active = button.dataset.place === activePlace;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    if (map) renderMarkers();
  }

  function showNearby() {
    if (!anchor || !map) return;
    const meters = Number(radius.value);
    const items = photos.filter(photo => photo.coordinates && map.distance(anchor.coordinates, photo.coordinates) <= meters);
    showPhotos(items, `${anchor.name} · nearby`, anchor.placeId);
    if (radiusCircle) radiusCircle.remove();
    radiusCircle = L.circle(anchor.coordinates, { radius: meters, color: "#bc3926", weight: 1, fillOpacity: 0.05, interactive: false }).addTo(map);
  }

  function clearRadius() {
    anchor = null;
    if (radiusCircle) radiusCircle.remove();
    radiusCircle = null;
  }

  placeButtons.forEach(button => {
    button.disabled = false;
    button.addEventListener("click", () => {
      clearRadius();
      if (button.dataset.place === "all") {
        showPhotos(photos, "All photographs", "all");
        return;
      }
      const entry = indexEntries.get(button.dataset.place);
      const ids = new Set(entry?.photo_ids || []);
      const items = button.dataset.place === "unindexed"
        ? photos.filter(photo => !photo.country || !photo.city)
        : photos.filter(photo => ids.has(photo.id));
      showPhotos(items, entry?.name || "Location to add", button.dataset.place);
      const points = items.filter(photo => photo.coordinates).map(photo => photo.coordinates);
      if (map && points.length) map.fitBounds(points, { padding: [45, 45], maxZoom: 12, animate: !reducedMotion });
    });
  });

  // Ordinary links remain usable if dialog support or JavaScript is absent.
  if (typeof HTMLDialogElement !== "undefined" && typeof HTMLDialogElement.prototype.showModal === "function") {
    const dialog = document.createElement("dialog");
    dialog.className = "travel-lightbox";
    dialog.setAttribute("aria-label", "Travel photograph preview");
    dialog.innerHTML = '<div class="travel-lightbox-bar"><span class="travel-lightbox-position"></span><div><button type="button" aria-label="Previous photograph">←</button><button type="button" aria-label="Next photograph">→</button><button type="button" aria-label="Close photograph preview">Close ×</button></div></div><img alt=""><p class="travel-lightbox-caption"></p><time class="travel-lightbox-date"></time>';
    document.body.append(dialog);
    const [previous, next, close] = dialog.querySelectorAll("button");
    let index = 0;
    function display() {
      const photo = visible[index];
      const preview = dialog.querySelector("img");
      preview.src = cards.get(photo.id).querySelector("a").href;
      preview.alt = photo.alt;
      dialog.querySelector(".travel-lightbox-caption").textContent = `${photo.place} — ${photo.alt}${photo.location_note ? ` · ${photo.location_note}` : ""}`;
      const date = dialog.querySelector("time");
      date.textContent = photo.date || "";
      date.dateTime = photo.date || "";
      dialog.querySelector(".travel-lightbox-position").textContent = `${index + 1} / ${visible.length}`;
      previous.disabled = next.disabled = visible.length < 2;
    }
    function step(delta) { index = (index + delta + visible.length) % visible.length; display(); }
    previous.addEventListener("click", () => step(-1));
    next.addEventListener("click", () => step(1));
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("keydown", event => {
      if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
    });
    dialog.addEventListener("click", event => {
      const box = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
    });
    cards.forEach((card, id) => card.querySelector("a").addEventListener("click", event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      index = visible.findIndex(photo => photo.id === id);
      display();
      dialog.showModal();
    }));
  }

  if (typeof L === "undefined") {
    document.querySelector(".travel-map-fallback").textContent = "The map could not load. Choose a place or browse the photographs below.";
    return;
  }
  document.querySelector(".travel-map-fallback").remove();
  map = L.map("travel-map", { scrollWheelZoom: true, minZoom: 1, maxZoom: 19, zoomAnimation: !reducedMotion, fadeAnimation: !reducedMotion, maxBounds: [[-85, -180], [85, 180]], maxBoundsViscosity: 1 });
  map.setView([24, 10], document.getElementById("travel-map").clientWidth < 550 ? 1 : 2);
  const basemapUnavailable = () => {
    status.hidden = false;
    status.textContent = "The basemap could not load. Place buttons and photographs are still available.";
  };
  // Vector boundaries can be styled independently of the coast and land.
  // Raster OSM tiles bake maritime borders into the image itself.
  try {
    if (typeof maplibregl === "undefined" || !L.maplibreGL) throw new Error("Vector map unavailable");
    const basemap = L.maplibreGL({
      style: "https://tiles.openfreemap.org/styles/liberty",
      attribution: '<a href="https://openfreemap.org/">OpenFreeMap</a> · &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> · &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map).getMaplibreMap();
    basemap.on("style.load", () => {
      if (basemap.getLayer("water")) basemap.setPaintProperty("water", "fill-color", "#aad3df");
      basemap.getStyle().layers.forEach(layer => {
        if (layer["source-layer"] === "boundary") {
          const landOnly = ["!=", ["get", "maritime"], 1];
          basemap.setFilter(layer.id, layer.filter ? ["all", layer.filter, landOnly] : landOnly);
        }
      });
    });
    basemap.on("error", basemapUnavailable);
  } catch (_) {
    basemapUnavailable();
  }
  markers = L.layerGroup().addTo(map);
  const located = photos.filter(photo => photo.coordinates);

  function renderMarkers() {
    if (!markers) return;
    markers.clearLayers();
    const groups = [];
    located.forEach(photo => {
      const point = map.project(photo.coordinates);
      let group = groups.find(candidate => candidate.point.distanceTo(point) < 44);
      if (!group) { group = { point, photos: [] }; groups.push(group); }
      group.photos.push(photo);
    });
    const selectedIds = new Set(visible.map(photo => photo.id));
    groups.forEach(group => {
      const first = group.photos[0];
      const label = group.photos.length === 1 ? first.place : `${group.photos.length} photographs · click to explore`;
      const active = visible.length !== photos.length && group.photos.some(photo => selectedIds.has(photo.id));
      const icon = L.divIcon({ className: `travel-pin${active ? " is-selected" : ""}`, html: `<span>${group.photos.length}</span>`, iconSize: [36, 36], iconAnchor: [18, 18] });
      const marker = L.marker(first.coordinates, { icon, title: label, keyboard: true }).addTo(markers);
      const tooltip = document.createElement("span");
      tooltip.textContent = label + (group.photos.some(photo => photo.location_source === "manual") ? " · Includes manually located photographs" : "");
      marker.bindTooltip(tooltip, { direction: "top" });
      const element = marker.getElement();
      element?.setAttribute("aria-label", label);
      marker.on("click", () => {
        clearRadius();
        const spread = Math.max(...group.photos.map(photo => map.distance(first.coordinates, photo.coordinates)));
        if (group.photos.length > 1 && spread > Number(radius.value)) {
          showPhotos(group.photos, "Places in this area");
          map.fitBounds(group.photos.map(photo => photo.coordinates), { padding: [65, 65], maxZoom: 16, animate: !reducedMotion });
        } else {
          anchor = { coordinates: first.coordinates, name: first.place, placeId: first.place_id };
          showNearby();
          if (map.getZoom() < 13) map.setView(first.coordinates, 13, { animate: !reducedMotion });
        }
      });
    });
  }
  map.on("zoomend", renderMarkers);
  const world = () => map.setView([24, 10], document.getElementById("travel-map").clientWidth < 550 ? 1 : 2, { animate: !reducedMotion });
  world();
  renderMarkers();
  radius.disabled = true;
  radius.addEventListener("change", showNearby);
  const worldButton = document.getElementById("travel-world");
  const fitButton = document.getElementById("travel-fit");
  worldButton.disabled = false;
  fitButton.disabled = located.length === 0;
  worldButton.addEventListener("click", world);
  fitButton.addEventListener("click", () => map.fitBounds(located.map(photo => photo.coordinates), { padding: [55, 55], maxZoom: 15, animate: !reducedMotion }));
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(() => map.invalidateSize()).observe(document.getElementById("travel-map"));
})();
