<template>
    <div class="d-flex flex-column fill-height">
        <div class="d-flex justify-space-between align-center pa-2">
            <div class="d-flex ga-2 align-center">
                <v-icon-btn v-if="!doCombineActionButtons" icon="mdi-cog" v-ripple @click="openSettings" />
                <v-chip>
                    <p>{{ getNumSolvedCities() }} / {{ markers.length }}</p>
                    <v-divider class="ml-2 mr-2" vertical inset></v-divider>
                    <p>{{ getPointsPercentage() + "%" }}</p>
                </v-chip>
            </div>
            <div v-if="!didFinish && nextMarkerIndex !== -1" class="d-flex ga-2 align-center">
                <p v-if="!doCombineActionButtons" class="ma-0">Kattints:</p>
                <v-chip :text="markers[nextMarkerIndex].name"></v-chip>
            </div>  
            <div class="d-flex ga-2 align-center">
                <v-chip :text="elapsedTime"></v-chip>
                <v-icon-btn v-if="!doCombineActionButtons" icon="mdi-reload" v-ripple @click="restartButtonClicked" />
                <v-menu v-model="isButtonMenuOpen" v-else location="bottom end">
                    <template #activator="{ props }">
                        <v-icon-btn
                        v-bind="props"
                        icon="mdi-dots-vertical"
                        v-ripple
                        />
                    </template>

                    <v-list class="pa-0" rounded="xl">
                        <v-list-item @click="restartButtonClicked" prepend-icon="mdi-refresh">
                            <v-list-item-title>Újrakezdés</v-list-item-title>
                        </v-list-item>

                        <v-list-item @click="openSettings" prepend-icon="mdi-cog">
                            <v-list-item-title>Beállítások</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </div>
        </div>
        <v-card v-show="panzoomInstance" class="d-flex flex-grow-1 align-center justify-center w-100 pa-0" elevation="4">
            <div ref="zoomContent" class="d-flex align-center justify-center w-100 h-100" style="touch-action: manipulation;">
                <div class="position-relative d-inline-block zoom-container">
                    <img
                        ref="map"
                        src="@/assets/hungaryCities.png"
                        alt="Map"
                        class="d-block map-image"
                    />
    
                    <div
                        v-for="marker in markers"
                        class="position-absolute"
                        :style="markerRelativePositioning(marker)"
                    >
                        <img
                            v-if="!doHideMarkers || (marker.numFailedGuesses >= 3 && marker.state !== MarkerState.Solved)"
                            class="d-block marker-icon"
                            :src="markerPaths[marker.state]"
                            :style="getMarkerIconFilter(marker)"
                        />

                        <p
                            v-if="marker.name === wrongMarkerName"
                            class="text-red ma-0 text-center position-absolute"
                            style="
                                left: 50%;
                                top: 5px;
                                transform: translateX(-50%);
                                white-space: nowrap;
                                font-size: smaller;
                                pointer-events: none;
                            "
                        >
                            {{ marker.name }}
                        </p>
                    </div>
                </div>
            </div>
        </v-card>
    </div>
    <v-dialog v-model="isResultsDialogOpen" max-width="500">
        <v-card class="d-flex" :title="didRunOutOfTime ? 'Sajnos lejárt az idő' : 'Szép munka'" rounded="xl">
            <div class="d-flex justify-center">
                <div class="d-flex flex-column">
                    <div class="d-flex ml-10 mr-10 flex-wrap">
                        <div v-if="didRunOutOfTime" class="d-flex ga-2 align-center mr-5">
                            <p>Bejelölt városok</p>
                            <v-chip>
                                <p>{{ getNumSolvedCities() }} / {{ markers.length }}</p>
                            </v-chip>
                        </div>
                        <div class="d-flex ga-2 align-center mr-5">
                            <p>Elért pontszám:</p>
                            <v-chip size="large" :color="getPercentageColor(getPointsPercentage())">
                                {{ getPointsPercentage() + "%" }}
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
                        <v-btn class="ma-2" text="Bezárás" prepend-icon="mdi-arrow-left" rounded="pill" variant="tonal" @click="closeResultsDialog"></v-btn>
                        <v-btn class="ma-2" text="Újrakezdés" prepend-icon="mdi-reload" rounded="pill" variant="tonal" @click="resetQuiz"></v-btn>
                    </v-card-actions>
                </div>
            </div>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isRestartDialogOpen" max-width="400">
        <v-card title="Megerősítés" text="Biztosan újra akarod kezdeni?" rounded="xl">
            <div class="pa-3">
                <v-card-actions class="d-flex justify-space-between">
                    <v-btn text="Vissza" prepend-icon="mdi-arrow-left" rounded="pill" variant="tonal" @click="closeRestartDialog"></v-btn>
                    <v-btn text="Újrakezdés" prepend-icon="mdi-reload" rounded="pill" variant="tonal" @click="resetQuiz"></v-btn>
                </v-card-actions>
            </div>
        </v-card>
    </v-dialog>
    <v-dialog v-model="isSettingsOpen" max-width="500">
        <v-card class="d-flex" title="Beállítások" rounded="xl">
            <div class="pa-3">
                <div class="ml-7">
                    <v-switch v-model="doHideMarkers" density="compact" label="Város jelzések elrejtése"></v-switch>
                    <v-switch v-model="isTimeLimitEnabled" density="compact" label="5 perces időlimit"></v-switch>
                </div>
                <v-card-actions class="d-flex justify-left">
                    <v-btn text="Vissza" prepend-icon="mdi-arrow-left" rounded="pill" variant="tonal" @click="isSettingsOpen = false"></v-btn>
                </v-card-actions>
            </div>
        </v-card>
    </v-dialog>
</template>

<script setup>
    import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
    import { useIntervalFn } from '@vueuse/core'
    import { useDisplay } from 'vuetify'
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
    const isSettingsOpen = ref(false);
    const isButtonMenuOpen = ref(false);
    const didFinish = ref(false);
    const didRunOutOfTime = ref(false);
    const doHideMarkers = ref(false);
    const isTimeLimitEnabled = ref(false);
    const nextMarkerIndex = ref(-1);
    const wrongMarkerName = ref("");

    let dragStart = new Point(0, 0);
    let panzoomInstance = null;

    function padNum(num) {
        return num.toString().padStart(2, "0");
    }

    const { width: viewportWidth } = useDisplay()

    const doCombineActionButtons = computed(
        () => {
            return viewportWidth.value < 550;
        }
    )

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

    const numPoints = computed(
        () => {
            let points = 0;
            markers.value.forEach((city) => {
                if (city.state == MarkerState.Solved && city.numFailedGuesses === 0) {
                    points++;
                }
            });
            return points;
        }
    )

    watch(isResultsDialogOpen, value => {
        if (value) {
            didFinish.value = true;
        }
    });

    watch([isRestartDialogOpen, isSettingsOpen], ([value1, value2]) => {
        if (value1 || value2) {
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

    const { pause: pauseTimer, resume: resumeTimer } = useIntervalFn(
        () => { 
            if (isTimeLimitEnabled.value && elapsedSeconds.value >= 5 * 60) {
                didFinish.value = true;
                didRunOutOfTime.value = true;
                isResultsDialogOpen.value = true;
                pauseTimer();
            }
            else {
                elapsedSeconds.value++;
            }
        },
        1000,
        { immediate: false }
    )

    onMounted(() => {
        markers.value = cities.map(city => ({
            name: city.name,
            pos: new Point(city.position[0], city.position[1]),
            state: MarkerState.Unsolved,
            numFailedGuesses: 0
        }))
        
        getNextMarker();

        panzoomInstance = panzoom(zoomContent.value, {
            maxZoom: 4,
            minZoom: 1,
            bounds: true,
            boundsPadding: 0.5,
        });

        zoomContent.value.addEventListener("mousemove", onMouseMove);
        zoomContent.value.addEventListener("mouseup", onMouseRelease);
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

    function getPointsPercentage() {
        if (getNumSolvedCities() === 0) {
            return 0;
        }
        else {
            return Math.round((numPoints.value / getNumSolvedCities()) * 100);
        }
    }

    function getNumSolvedCities() {
        let numSolvedCities = 0;
        markers.value.forEach((value) => {
            if (value.state === MarkerState.Solved) {
                numSolvedCities++;
            }
        });
        return numSolvedCities;
    }

    function getPercentageColor(percentage) {
        if (percentage < 25) {
            return "red";
        }
        else if (percentage < 50) {
            return "orange";
        }
        else if (percentage < 75) {
            return "yellow";
        }
        else {
            return "green";
        }
    }

    function markerRelativePositioning(marker) {
        if (!map.value) return {}

        return {
            left: ((marker.pos.x - 7.5) / map.value.naturalWidth) * 100 + '%',
            top: ((marker.pos.y- 7.5) / map.value.naturalHeight) * 100 + '%',
        }
    }

    function getMarkerIconFilter(marker) {
        let filter = "grayscale(100%) brightness(500%)";
        if (marker.numFailedGuesses === 0) {
            filter = "grayscale(100%) brightness(500%)";
        }
        else if (marker.numFailedGuesses <= 2) {
            if (marker.state === MarkerState.Solved) {
                filter = "hue-rotate(60deg) brightness(400%)";
            }
        }
        else {
            filter = "";
        }

        return {
            "filter": filter
        };
    }

    function distance2(point1, point2) {
        return Math.pow(point2.x - point1.x, 2) + Math.pow(point2.y - point1.y, 2);
    }

    function getDistanceSortedMarkers(point) {
        const sortedMarkers = markers.value.toSorted((a, b) => {
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

        return sortedMarkers;
    }

    function getClosestMarker(mousePos) {
        const sortedMarkers = getDistanceSortedMarkers(mousePos);
        const closestMarker = sortedMarkers[0];
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
        if (event.buttons !== 0) {
            isButtonMenuOpen.value = false;
        }
        const imagePos = getMouseImagePos(getEventPos(event));

        markers.value.forEach(marker => {
            if (marker.state === MarkerState.Hovered) {
                marker.state = MarkerState.Unsolved;
            }
        });

        if (didRunOutOfTime.value) {
            return;
        } 

        const closestMarker = getClosestMarker(imagePos);
        if (closestMarker) {
            closestMarker.state = MarkerState.Hovered;
        }
    }

    function onMouseRelease(event) {
        const imagePos = getMouseImagePos(getEventPos(event));

        const closestMarker = getClosestMarker(imagePos);

        if (!closestMarker) {
            if (doHideMarkers) {
                markers.value[nextMarkerIndex.value].numFailedGuesses++;
            }
            return;
        }

        if (didRunOutOfTime.value) {
            return;
        }

        wrongMarkerName.value = "";

        if (closestMarker.name === markers.value[nextMarkerIndex.value].name) {
            closestMarker.state = MarkerState.Solved;
            getNextMarker();

            if (markers.value.length === getNumSolvedCities()) {
                didFinish.value = true;
                isResultsDialogOpen.value = true;
                pauseTimer();
            }
        }
        else {
            markers.value[nextMarkerIndex.value].numFailedGuesses++;
            wrongMarkerName.value = closestMarker.name;
        }
    }

    function onDragStart(event) {
        isButtonMenuOpen.value = false;
        const dragStartEvent = event.touches[0];
        dragStart = getEventPos(dragStartEvent);
    }

    function onDragEnd(event) {
        const dragEndEvent = event.changedTouches[0];
        const dragEnd = getEventPos(dragEndEvent);
        if (distance2(dragStart, dragEnd) < Math.pow(dragDistanceTreshold, 2)) {
            onMouseRelease(dragEndEvent);
        }
    }

    function getNextMarker() {
        const unsolvedMarkers = markers.value.map((value, index) => (
            {
                value: value,
                index: index
            }
        )).filter((element) => element.value.state === MarkerState.Unsolved);

        if (unsolvedMarkers.length) {
            nextMarkerIndex.value = unsolvedMarkers[Math.floor(Math.random() * unsolvedMarkers.length)].index;
        }
    }

    function closeResultsDialog() {
        isResultsDialogOpen.value = false;
    }
    
    function restartButtonClicked() {
        isRestartDialogOpen.value = true;
    }

    function openSettings() {
        isSettingsOpen.value = true;
    }

    function closeRestartDialog() {
        isRestartDialogOpen.value = false;
    }

    function resetQuiz() {
        isRestartDialogOpen.value = false;
        isResultsDialogOpen.value = false;
        isButtonMenuOpen.value = false;

        wrongMarkerName.value = "";
        didFinish.value = false;
        didRunOutOfTime.value = false;
        markers.value.forEach((marker) => {
            marker.state = MarkerState.Unsolved;
            marker.numFailedGuesses = 0;
        });

        getNextMarker();
        panzoomInstance.moveTo(0, 0);
        panzoomInstance.zoomAbs(0, 0, 1);
        elapsedSeconds.value = 0;
        resumeTimer();
    }
</script>
<style>
    .marker-icon {
        width: 15px;
        height: 15px;
        pointer-events: none;
    }

    .map-image {
        width: 600px;
        height: 414px;
    }

    .map-container {
        overflow: auto;
        width: 100%;
        height: 100%
    }
</style>
