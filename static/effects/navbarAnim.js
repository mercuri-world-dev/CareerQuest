const navbar = document.querySelector('.vertical-navbar');
const navItems = document.querySelectorAll('.nav-link');
const navPath = document.getElementById('navbarPath');
const navDrawPath = document.getElementById('navbarDrawPath');

function setNavPath(yShift, addedWidth=0) {
  const topOffset = yShift;
  const bottomOffset = yShift+addedWidth;

  const centerOffset = topOffset + ((bottomOffset - topOffset) / 2);

  const adjustedPath = `M152 ${246+topOffset}H151.862C151.862 ${262.91+topOffset} 138.154 ${276.618+topOffset} 121.244 ${276.618+topOffset}H43.6221C26.158 ${276.618+topOffset} 12.0001 ${290.775+topOffset} 12 ${308.239+centerOffset}C12 ${325.703+bottomOffset} 26.1579 ${339.861+bottomOffset} 43.6221 ${339.861+bottomOffset}H115.723C135.682 ${339.861+bottomOffset} 151.862 ${356.041+bottomOffset} 151.862 ${376+bottomOffset}H152V3010C152 3026.016 139.016 3039 123 3039H0V0H152V246Z`;

  navDrawPath.setAttribute('d', adjustedPath);
}

setNavPath(-100, -20);

navItems.forEach(item => {
  const topCutout = 276.618; // absolute coords of top of path coordinate
  const itemRect = item.getBoundingClientRect();
  const centerItemOffset = itemRect.top - topCutout;
  item.addEventListener('mouseover', () => {
    setNavPath(centerItemOffset);
  });
  item.addEventListener('mouseleave', () => {
    navPath.setAttribute('transform', `translate(0, 0)`);
  });
});

// `M152 ${246+topOffset}H151.862C151.862 ${262.91+topOffset} 138.154 ${276.618+topOffset} 121.244 ${276.618+topOffset}H43.6221C26.158 ${276.618+topOffset} 12.0001 ${290.775+topOffset} 12 ${308.239+centerOffset}C12 ${325.703+bottomOffset} 26.1579 ${339.861+bottomOffset} 43.6221 ${339.861+bottomOffset}H115.723C135.682 ${339.861+bottomOffset} 151.862 ${356.041+bottomOffset} 151.862 ${376+bottomOffset}H152V3010C152 3026.016 139.016 3039 123 3039H0V0H152V246Z`

// M152
// 246H151.862C151.862 // top right curve
// 262.91 // top right curve
// 138.154 
// 276.618 // top right curve
// 121.244 
// 276.618H43.6221C26.158 // top line
// 276.618 // top left curve
// 12.0001 
// 290.775 // top left curve
// 12 
// 308.239C12 // !! center of left curve
// 325.703 // bottom left curve
// 26.1579 
// 339.861 // bottom left curve
// 43.6221 
// 339.861H115.723C135.682 // bottom line
// 339.861 // bottom right curve
// 151.862 
// 356.041 // bottom right curve
// 151.862 
// 376H152V3010C152 // bottom right curve
// 3026.016 
// 139.016 
// 3039 
// 123 
// 3039H0V0H152V246Z