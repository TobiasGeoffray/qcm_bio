// Pixel Art Creator - Logic

document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const GRID_SIZES = {
        16: { cols: 16, rows: 16 },
        32: { cols: 32, rows: 32 },
        48: { cols: 48, rows: 48 },
        64: { cols: 64, rows: 64 }
    };

    // État de l'application
    let state = {
        currentColor: '#000000',
        gridSize: 32,
        isFilling: false,
        pixels: {},
        useTransparentBg: true
    };

    // Éléments DOM
    const gridContainer = document.getElementById('pixelart-grid');
    const colorPalette = document.getElementById('color-palette');
    const sizeOptions = document.querySelectorAll('.size-option');
    const fillTool = document.getElementById('fill-tool');
    const clearTool = document.getElementById('clear-tool');
    const invertTool = document.getElementById('invert-tool');
    const saveButton = document.getElementById('save-pixelart');
    const previewButton = document.getElementById('preview-pixelart');
    const previewSection = document.getElementById('preview-section');
    const previewCanvas = document.getElementById('pixelart-preview');
    const messageDiv = document.getElementById('pixelart-message');
    const transparentBgCheckbox = document.getElementById('transparent-bg');

    // Initialisation
    function init() {
        // Charger la grille avec la taille par défaut
        createGrid(state.gridSize);
        
        // Sélectionner la première couleur par défaut
        const firstColor = colorPalette.querySelector('.color-option');
        if (firstColor) {
            selectColor(firstColor);
        }

        // Activer la taille sélectionnée
        updateSizeButtons();
        
        // Lire l'état de la checkbox
        if (transparentBgCheckbox) {
            state.useTransparentBg = transparentBgCheckbox.checked;
        }

        // Ajouter les écouteurs d'événements
        setupEventListeners();
    }

    // Créer la grille de pixels
    function createGrid(size) {
        const { cols, rows } = GRID_SIZES[size];
        
        // Vider la grille actuelle
        gridContainer.innerHTML = '';
        
        // Mettre à jour le CSS Grid - auto pour s'adapter à la taille des pixels
        gridContainer.style.gridTemplateColumns = `repeat(${cols}, auto)`;
        
        // Créer les nouveaux pixels
        for (let i = 0; i < cols * rows; i++) {
            const pixel = document.createElement('div');
            pixel.className = 'pixel';
            pixel.dataset.index = i;
            
            // Récupérer la couleur sauvegardée si elle existe
            const key = `${cols}x${rows}_${i}`;
            const color = state.pixels[key] || 'transparent';
            pixel.style.backgroundColor = color;
            
            pixel.addEventListener('click', function() {
                handlePixelClick(i, pixel);
            });
            
            pixel.addEventListener('mousedown', function(e) {
                e.preventDefault();
                handlePixelClick(i, pixel);
            });
            
            pixel.addEventListener('mouseenter', function(e) {
                if (e.buttons === 1) { // Bouton gauche maintenu
                    handlePixelClick(i, pixel);
                }
            });
            
            gridContainer.appendChild(pixel);
        }
        
        // Sauvegarder la configuration
        state.gridSize = size;
    }

    // Gérer le clic sur un pixel
    function handlePixelClick(index, pixelElement) {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        const key = `${cols}x${rows}_${index}`;
        
        if (state.isFilling) {
            // Remplir avec la couleur actuelle
            pixelElement.style.backgroundColor = state.currentColor;
            state.pixels[key] = state.currentColor;
        } else if (state.currentColor === 'transparent') {
            // Effacer
            pixelElement.style.backgroundColor = 'transparent';
            delete state.pixels[key];
        } else {
            // Définir la couleur
            pixelElement.style.backgroundColor = state.currentColor;
            state.pixels[key] = state.currentColor;
        }
    }

    // Sélectionner une couleur
    function selectColor(colorElement) {
        // Retirer la classe active de tous les éléments
        colorPalette.querySelectorAll('.color-option').forEach(el => {
            el.classList.remove('active');
        });
        
        // Ajouter la classe active à l'élément sélectionné
        colorElement.classList.add('active');
        
        // Mettre à jour la couleur actuelle
        state.currentColor = colorElement.dataset.color;
    }

    // Mettre à jour les boutons de taille
    function updateSizeButtons() {
        sizeOptions.forEach(btn => {
            if (parseInt(btn.dataset.size) === state.gridSize) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Effacer toute la grille
    function clearGrid() {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        const pixels = gridContainer.querySelectorAll('.pixel');
        
        pixels.forEach((pixel, index) => {
            pixel.style.backgroundColor = 'transparent';
            const key = `${cols}x${rows}_${index}`;
            delete state.pixels[key];
        });
        
        showMessage('Grille effacée', 'success');
    }

    // Remplir toute la grille avec la couleur actuelle
    function fillGrid() {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        const pixels = gridContainer.querySelectorAll('.pixel');
        
        pixels.forEach((pixel, index) => {
            pixel.style.backgroundColor = state.currentColor;
            const key = `${cols}x${rows}_${index}`;
            state.pixels[key] = state.currentColor;
        });
        
        showMessage('Grille remplie', 'success');
    }

    // Inverser les couleurs
    function invertColors() {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        const pixels = gridContainer.querySelectorAll('.pixel');
        
        pixels.forEach((pixel, index) => {
            const currentColor = pixel.style.backgroundColor || 'transparent';
            const inverted = invertColor(currentColor);
            pixel.style.backgroundColor = inverted;
            const key = `${cols}x${rows}_${index}`;
            state.pixels[key] = inverted;
        });
        
        showMessage('Couleurs inversées', 'success');
    }

    // Inverser une couleur hexadécimale
    function invertColor(hex) {
        if (hex === 'transparent' || hex === '#FFFFFF') {
            return '#000000';
        }
        if (hex === '#000000') {
            return '#FFFFFF';
        }
        
        // Convertir en RGB
        let r, g, b;
        if (hex.startsWith('#')) {
            hex = hex.substring(1);
            if (hex.length === 3) {
                r = parseInt(hex[0] + hex[0], 16);
                g = parseInt(hex[1] + hex[1], 16);
                b = parseInt(hex[2] + hex[2], 16);
            } else {
                r = parseInt(hex.substring(0, 2), 16);
                g = parseInt(hex.substring(2, 4), 16);
                b = parseInt(hex.substring(4, 6), 16);
            }
        } else if (hex.startsWith('rgb(')) {
            const match = hex.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
            if (match) {
                r = parseInt(match[1]);
                g = parseInt(match[2]);
                b = parseInt(match[3]);
            }
        }
        
        // Inverser
        r = 255 - r;
        g = 255 - g;
        b = 255 - b;
        
        // Convertir en hexadécimal
        const toHex = (c) => {
            const hex = c.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        };
        
        return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
    }

    // Prévisualiser l'image
    function previewImage() {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        
        // Créer un canvas
        const canvas = previewCanvas;
        const ctx = canvas.getContext('2d');
        
        // Définir la taille du canvas (10x la taille de la grille)
        const pixelSize = 10;
        canvas.width = cols * pixelSize;
        canvas.height = rows * pixelSize;
        
        // Effacer ou remplir selon l'option
        if (state.useTransparentBg) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        } else {
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        // Dessiner les pixels
        const pixels = gridContainer.querySelectorAll('.pixel');
        pixels.forEach((pixel, index) => {
            const color = pixel.style.backgroundColor || 'transparent';
            const row = Math.floor(index / cols);
            const col = index % cols;
            
            // Ne dessiner que les pixels non transparents (pour fond transparent)
            if (color !== 'transparent' && color !== '' && color !== 'rgba(0, 0, 0, 0)') {
                ctx.fillStyle = color;
                ctx.fillRect(col * pixelSize, row * pixelSize, pixelSize, pixelSize);
            }
        });
        
        // Afficher la prévisualisation
        previewSection.style.display = 'block';
        
        showMessage('Prévisualisation générée', 'success');
    }

    // Exporter l'image comme PNG
    function exportAsPNG() {
        const { cols, rows } = GRID_SIZES[state.gridSize];
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Taille finale (1 pixel = 1 pixel pour conserver la résolution exacte)
        const pixelSize = 1;
        canvas.width = cols * pixelSize;
        canvas.height = rows * pixelSize;
        
        // Effacer le canvas (fond transparent par défaut)
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Dessiner les pixels
        const pixels = gridContainer.querySelectorAll('.pixel');
        pixels.forEach((pixel, index) => {
            const color = pixel.style.backgroundColor || 'transparent';
            const row = Math.floor(index / cols);
            const col = index % cols;
            
            // Ne dessiner que les pixels non transparents/blancs (pour fond transparent)
            if (color !== 'transparent' && color !== '' && color !== '#FFFFFF' && color !== 'rgba(255, 255, 255, 1)' && color !== 'rgba(0, 0, 0, 0)') {
                ctx.fillStyle = color;
                ctx.fillRect(col * pixelSize, row * pixelSize, pixelSize, pixelSize);
            }
        });
        
        return canvas;
    }

    // Sauvegarder l'image
    function savePixelArt() {
        const name = document.getElementById('pixelart-name').value.trim() || 'pixelart_' + new Date().getTime();
        const canvas = exportAsPNG();
        
        showMessage('Enregistrement en cours...', 'info');
        
        // Convertir en blob et envoyer au serveur
        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('image', blob, name + '.png');
            formData.append('name', name);
            
            fetch(window.flaskPaths.saveUrl, {
                method: 'POST',
                body: formData,
                credentials: 'include',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                // Vérifier si la réponse est du JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json();
                } else {
                    // Si ce n'est pas du JSON, essayer de lire le texte pour déboguer
                    return response.text().then(text => {
                        throw new Error('Réponse du serveur non-JSON: ' + text.substring(0, 100));
                    });
                }
            })
            .then(data => {
                if (data && data.success) {
                    showMessage('Pixel art enregistré avec succès !', 'success');
                    // Réinitialiser le nom
                    document.getElementById('pixelart-name').value = 'pixelart_' + new Date().getTime();
                } else {
                    showMessage('Erreur : ' + (data && data.error ? data.error : 'Inconnu'), 'error');
                }
            })
            .catch(error => {
                showMessage('Erreur lors de l\'enregistrement : ' + error.message, 'error');
            });
        }, 'image/png');
    }

    // Afficher un message
    function showMessage(text, type = 'info') {
        messageDiv.textContent = text;
        messageDiv.style.color = type === 'error' ? '#ff6b6b' : '#d4edda';
        
        // Effacer après 3 secondes
        setTimeout(() => {
            messageDiv.textContent = '';
        }, 3000);
    }

    // Configurer les écouteurs d'événements
    function setupEventListeners() {
        // Sélection de couleur
        colorPalette.querySelectorAll('.color-option').forEach(colorEl => {
            colorEl.addEventListener('click', function() {
                selectColor(this);
                state.isFilling = false;
            });
        });

        // Sélection de taille
        sizeOptions.forEach(btn => {
            btn.addEventListener('click', function() {
                const newSize = parseInt(this.dataset.size);
                if (newSize !== state.gridSize) {
                    // Demander confirmation
                    if (confirm('Changer la taille de la grille effacera votre travail actuel. Continuer ?')) {
                        state.gridSize = newSize;
                        createGrid(newSize);
                        updateSizeButtons();
                    }
                }
            });
        });

        // Bouton Remplir
        if (fillTool) {
            fillTool.addEventListener('click', function() {
                state.isFilling = true;
                showMessage('Outils : Remplissage activé. Cliquez sur la grille.', 'info');
            });
        }

        // Bouton Tout effacer
        if (clearTool) {
            clearTool.addEventListener('click', function() {
                if (confirm('Voulez-vous vraiment effacer toute la grille ?')) {
                    clearGrid();
                }
            });
        }

        // Bouton Inverser
        if (invertTool) {
            invertTool.addEventListener('click', function() {
                invertColors();
            });
        }

        // Bouton Prévisualiser
        if (previewButton) {
            previewButton.addEventListener('click', function() {
                previewImage();
            });
        }

        // Bouton Enregistrer
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                savePixelArt();
            });
        }

        // Gestion du glisser-déposer pour éviter les comportements indésirables
        gridContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
        });

        gridContainer.addEventListener('drop', function(e) {
            e.preventDefault();
        });
    }

    // Initialiser l'application
    init();
});
