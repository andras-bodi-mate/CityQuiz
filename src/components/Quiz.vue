<template>
    <div class="d-flex flex-column fill-height">
        <div class="d-flex justify-space-between align-center pa-2">
            <v-chip>
                <p>{{ numSolvedCities }} / {{ markers.length }}</p>
                <v-divider class="ml-2 mr-2" vertical inset></v-divider>
                <p>{{ solvedPercentage }}</p>
            </v-chip>
            <div class="d-flex ga-2 align-center">
                <p class="d-none d-sm-block ma-0">Kattints:</p>
                <v-chip text="Miskolc"></v-chip>
            </div>
            <div class="d-flex ga-2 align-center">
                <v-chip :text="elapsedTime"></v-chip>
                <v-icon-btn icon="mdi-reload" v-ripple @click="restartButtonClicked">
                </v-icon-btn>
            </div>
        </div>
        <v-card class="d-flex flex-grow-1 align-center justify-center w-100 pa-0" elevation="4">
            <div ref="zoomContent" class="d-flex align-center justify-center w-100 h-100" style="touch-action: manipulation;">
                <div class="position-relative d-inline-block">
                    <img
                        ref="map"
                        src="@/assets/hungaryCities.png"
                        alt="Map"
                        class="d-block"
                        style="max-width: 100%; max-height: 100%;"
                    />
    
                    <div
                        v-for="marker in markers"
                        class="position-absolute translate-middle"
                        :style="asRelativeCoordinates(marker)"
                    >
                        <img
                            :src="markerPaths[marker.state]"
                            class="d-block"
                            style="width: 15px; height: 15px; pointer-events: none;"
                        />
                    </div>
                </div>
            </div>
        </v-card>
    </div>
    <v-dialog v-model="isResultsDialogOpen" max-width="500">
        <v-card class="d-flex" title="Szép munka!" rounded="xl">
            <div class="d-flex justify-center">
                <div class="d-flex flex-column">
                    <div class="d-flex ml-10 mr-10 flex-wrap">
                        <div class="d-flex ga-2 align-center mr-5">
                            <p>Elért pontszám:</p>
                            <v-chip size="large" color="green">
                                {{ solvedPercentage }}
                            </v-chip>
                        </div>
                        <div class="d-flex ga-2 align-center">
                            <p>Eltelt idő:</p>
                            <v-chip size="large">
                                {{ elapsedTime }}
                            </v-chip>
                        </div>
                    </div>
                    <v-card-actions class="d-flex justify-space-between mt-5">
                        <v-btn class="ma-2" text="Bezárás" prepend-icon="mdi-close" rounded="pill" variant="tonal" @click="closeResultsDialog"></v-btn>
                        <v-btn class="ma-2" text="Újrakezdés" prepend-icon="mdi-reload" rounded="pill" variant="tonal" @click="resetQuiz"></v-btn>
                    </v-card-actions>
                </div>
            </div>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isRestartDialogOpen" max-width="500">
        <v-card title="Megerősítés" subtitle="Biztosan újra akarod kezdeni?" rounded="xl">
            <v-card-actions class="d-flex justify-space-between mt-5">
                <v-btn class="ma-2" text="Vissza" prepend-icon="mdi-close" rounded="pill" variant="tonal" @click="closeRestartDialog"></v-btn>
                <v-btn class="ma-2" text="Újrakezdés" prepend-icon="mdi-reload" rounded="pill" variant="tonal" @click="resetQuiz"></v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
    import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
    import { useIntervalFn } from '@vueuse/core'
    import panzoom from 'panzoom';
    import unsolved from '@/assets/markers/unsolved.svg';
    import hovered from '@/assets/markers/hovered.svg';
    import solved from '@/assets/markers/solved.svg';
    import cities from '@/assets/cities.json';

    class Point {
        constructor(x, y) {
            this.x = x;
            this.y = y;
        }
    }

    const MarkerState = {
        Unsolved: 0,
        Hovered: 1,
        Solved: 2
    }

    const markerPaths = {
        [MarkerState.Unsolved]: unsolved,
        [MarkerState.Hovered]: hovered,
        [MarkerState.Solved]: solved
    }

    const markers = ref([]);

    const hoverDistance = 10;
    const dragDistanceTreshold = 10;

    const zoomContent = ref(null);
    const map = ref(null);
    const elapsedSeconds = ref(0);
    const isResultsDialogOpen = ref(false);
    const isRestartDialogOpen = ref(false);
    const didFinish = ref(false);

    let dragStart = new Point(0, 0);
    let panzoomInstance = null;

    function padNum(num) {
        return num.toString().padStart(2, "0");
    }

    const elapsedTime = computed(
        () => {
            let remainingSeconds = elapsedSeconds.value;
            const hours = Math.floor(remainingSeconds / 3_600);
            remainingSeconds -= hours * 3_600;
            const minutes = Math.floor(remainingSeconds / 60);
            remainingSeconds -= minutes * 60;
            const seconds = Math.floor(remainingSeconds);
            let result = hours >= 1 ? `${padNum(hours)}:` : "";
            result += `${padNum(minutes)}:${padNum(seconds)}`;
            return result;
        }
    )

    const numSolvedCities = computed(
        () => {
            let unsolvedCities = 0;
            markers.value.forEach((city) => {
                if (city.state == MarkerState.Solved) {
                    unsolvedCities++;
                }
            });
            return unsolvedCities;
        }
    )

    const solvedPercentage = computed(
        () => {
            return `${Math.round((numSolvedCities.value / markers.value.length) * 100)}%`;
        }
    )

    watch(isResultsDialogOpen, (value, oldValue, onCleanup) => {
        if (value) {
            didFinish.value = true;
        }
    });

    watch(isRestartDialogOpen, (value, oldValue, onCleanup) => {
        if (value) {
            if (!didFinish.value) {
                pauseTimer();
            }
        }
        else {
            if (!didFinish.value) {
                resumeTimer();
            }
        }
    })

    const { pause: pauseTimer, resume: resumeTimer, isActive: isTimerActive} = useIntervalFn(
        () => { 
            elapsedSeconds.value++;
        },
        1000,
        { immediate: false }
    )

    onMounted(() => {
        markers.value = cities.slice(0, 3).map(city => ({
            name: city.name,
            pos: new Point(city.position[0], city.position[1]),
            state: MarkerState.Unsolved
        }))

        console.log(markers.value)

        panzoomInstance = panzoom(zoomContent.value, {
            maxZoom: 4,
            minZoom: 1,
            bounds: true,
            boundsPadding: 0.5,
        });

        zoomContent.value.addEventListener("mousemove", onMouseMove);
        zoomContent.value.addEventListener("mouseup", onMousePress);
        zoomContent.value.addEventListener("touchstart", onDragStart);
        zoomContent.value.addEventListener("touchend", onDragEnd);

        resumeTimer();
    });

    onBeforeUnmount(() => {
        if (panzoomInstance) {
            panzoomInstance.dispose();
        }
        if (map.value) {
        }
    });

    function asRelativeCoordinates(marker) {
        if (!map.value) return {};

        return {
            left: ((marker.pos.x - 7.5) / map.value.naturalWidth) * 100 + '%',
            top: ((marker.pos.y - 7.5) / map.value.naturalHeight) * 100 + '%'
        };
    }

    function distance2(point1, point2) {
        return Math.pow(point2.x - point1.x, 2) + Math.pow(point2.y - point1.y, 2);
    }

    function sortUnsolvedMarkersByDistance(point) {
        markers.value.sort((a, b) => {
            const aSolved = a.state === MarkerState.Solved;
            const bSolved = b.state === MarkerState.Solved;

            if (aSolved !== bSolved) {
                return aSolved ? 1 : -1;
            }

            if (!aSolved && !bSolved) {
                return (
                    distance2(a.pos, point) -
                    distance2(b.pos, point)
                );
            }

            return 0;
        });
    }

    function getClosestMarker(mousePos) {
        const closestMarker = markers.value[0];
        const transform = panzoomInstance.getTransform();
        const transformedHoverDistance = hoverDistance / transform.scale;
        if (closestMarker.state !== MarkerState.Solved &&
            distance2(closestMarker.pos, mousePos) < Math.pow(transformedHoverDistance, 2)
        ) {
            return closestMarker;
        }
        else {
            return null;
        }
    }

    function getMouseImagePos(eventPos) {
        if (!map.value) return [0, 0];
        const rect = map.value.getBoundingClientRect();

        // Mouse position relative to the container
        const relPos = new Point(
            eventPos.x - rect.left,
            eventPos.y - rect.top
        )

        // Get current panzoom transform
        const scale = new Point(
            map.value.naturalWidth / rect.width,
            map.value.naturalHeight / rect.height
        )

        const imagePos = new Point(
            relPos.x * scale.x,
            relPos.y * scale.y
        )
        return imagePos;
    }

    function getEventPos(event) {
        return new Point(
            event.clientX,
            event.clientY
        );
    }

    function onMouseMove(event) {
        const imagePos = getMouseImagePos(getEventPos(event));

        sortUnsolvedMarkersByDistance(imagePos);

        markers.value.forEach(marker => {
            if (marker.state === MarkerState.Hovered) {
                marker.state = MarkerState.Unsolved;
            }
        });

        const closestMarker = getClosestMarker(imagePos);
        if (closestMarker) {
            closestMarker.state = MarkerState.Hovered;
        }
    }

    function onMousePress(event) {
        const imagePos = getMouseImagePos(getEventPos(event));

        sortUnsolvedMarkersByDistance(imagePos);

        const closestMarker = getClosestMarker(imagePos);
        if (closestMarker) {
            closestMarker.state = MarkerState.Solved;
        }
        if (markers.value.length === numSolvedCities.value) {
            didFinish.value = true;
            isResultsDialogOpen.value = true;
            pauseTimer();
        }
    }

    function onDragStart(event) {
        const dragStartEvent = event.touches[0];
        dragStart = getEventPos(dragStartEvent);
        console.log(dragStart);
    }

    function onDragEnd(event) {
        const dragEndEvent = event.changedTouches[0];
        const dragEnd = getEventPos(dragEndEvent);
        if (distance2(dragStart, dragEnd) < Math.pow(dragDistanceTreshold, 2)) {
            onMousePress(dragEndEvent);
        }
    }

    function closeResultsDialog() {
        isResultsDialogOpen.value = false;
    }
    
    function restartButtonClicked() {
        isRestartDialogOpen.value = true;
    }

    function closeRestartDialog() {
        isRestartDialogOpen.value = false;
    }

    function resetQuiz() {
        isRestartDialogOpen.value = false;
        isResultsDialogOpen.value = false;
        didFinish.value = false;
        markers.value.forEach((marker) => {
            marker.state = MarkerState.Unsolved;
        });
        panzoomInstance.moveTo(0, 0);
        panzoomInstance.zoomAbs(0, 0, 1);
        elapsedSeconds.value = 0;
        resumeTimer();
    }
</script>