/* ===== Three.js 3D Educational Scene ===== */

function initThreeScene(containerId, options) {
    options = options || {};
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Respect reduced motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }
    
    // Reduce complexity on mobile
    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 50 : 150;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, container.offsetWidth / container.offsetHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: !isMobile });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    renderer.setPixelRatio(isMobile ? 1 : Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    
    camera.position.z = 30;
    
    // Particles
    const particleGeometry = new THREE.BufferGeometry();
    const particlePositions = [];
    const particleColors = [];
    const colorPalette = [
        new THREE.Color(0x7C3AED),
        new THREE.Color(0x2563EB),
        new THREE.Color(0x06B6D4),
        new THREE.Color(0x8B5CF6),
    ];
    
    for (let i = 0; i < particleCount; i++) {
        particlePositions.push(
            (Math.random() - 0.5) * 60,
            (Math.random() - 0.5) * 60,
            (Math.random() - 0.5) * 60
        );
        const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
        particleColors.push(color.r, color.g, color.b);
    }
    
    particleGeometry.setAttribute('position', new THREE.Float32BufferAttribute(particlePositions, 3));
    particleGeometry.setAttribute('color', new THREE.Float32BufferAttribute(particleColors, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
        size: 0.3,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
    });
    
    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);
    
    // AI Brain (wireframe sphere)
    const brainGeometry = new THREE.IcosahedronGeometry(5, 1);
    const brainMaterial = new THREE.MeshBasicMaterial({
        color: 0x8B5CF6,
        wireframe: true,
        transparent: true,
        opacity: 0.4,
    });
    const brain = new THREE.Mesh(brainGeometry, brainMaterial);
    scene.add(brain);
    
    // Inner brain glow
    const innerGeometry = new THREE.IcosahedronGeometry(3, 0);
    const innerMaterial = new THREE.MeshBasicMaterial({
        color: 0x06B6D4,
        wireframe: true,
        transparent: true,
        opacity: 0.3,
    });
    const innerBrain = new THREE.Mesh(innerGeometry, innerMaterial);
    scene.add(innerBrain);
    
    // Floating books (boxes)
    const books = [];
    const bookColors = [0x7C3AED, 0x2563EB, 0x06B6D4];
    for (let i = 0; i < (isMobile ? 3 : 6); i++) {
        const bookGeo = new THREE.BoxGeometry(2, 2.8, 0.4);
        const bookMat = new THREE.MeshBasicMaterial({
            color: bookColors[i % bookColors.length],
            wireframe: true,
            transparent: true,
            opacity: 0.5,
        });
        const book = new THREE.Mesh(bookGeo, bookMat);
        const angle = (i / 6) * Math.PI * 2;
        book.position.set(
            Math.cos(angle) * 12,
            Math.sin(angle) * 4,
            Math.sin(angle) * 8
        );
        book.rotation.z = angle;
        book.userData = { angle: angle, speed: 0.001 + Math.random() * 0.002 };
        books.push(book);
        scene.add(book);
    }
    
    // Graduation cap (cone)
    const capGeo = new THREE.ConeGeometry(3, 1, 4);
    const capMat = new THREE.MeshBasicMaterial({
        color: 0x2563EB,
        wireframe: true,
        transparent: true,
        opacity: 0.4,
    });
    const cap = new THREE.Mesh(capGeo, capMat);
    cap.position.set(15, 10, -5);
    scene.add(cap);
    
    // Mouse interaction
    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', function(e) {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = (e.clientY / window.innerHeight) * 2 - 1;
    });
    
    // Animation loop
    let animationId;
    function animate() {
        animationId = requestAnimationFrame(animate);
        
        // Rotate brain
        brain.rotation.x += 0.003;
        brain.rotation.y += 0.005;
        innerBrain.rotation.x -= 0.005;
        innerBrain.rotation.y -= 0.003;
        
        // Float books
        books.forEach(function(book, i) {
            book.position.y += Math.sin(Date.now() * 0.001 + i) * 0.01;
            book.rotation.y += book.userData.speed;
        });
        
        // Float cap
        cap.position.y = 10 + Math.sin(Date.now() * 0.0008) * 2;
        cap.rotation.y += 0.005;
        
        // Rotate particles
        particles.rotation.y += 0.0005;
        
        // Mouse-follow camera
        camera.position.x += (mouseX * 5 - camera.position.x) * 0.05;
        camera.position.y += (-mouseY * 5 - camera.position.y) * 0.05;
        camera.lookAt(scene.position);
        
        renderer.render(scene, camera);
    }
    animate();
    
    // Resize handler
    window.addEventListener('resize', function() {
        camera.aspect = container.offsetWidth / container.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.offsetWidth, container.offsetHeight);
    });
    
    // Cleanup on page hide
    document.addEventListener('visibilitychange', function() {
        if (document.hidden && animationId) {
            cancelAnimationFrame(animationId);
        } else if (!document.hidden) {
            animate();
        }
    });
}
