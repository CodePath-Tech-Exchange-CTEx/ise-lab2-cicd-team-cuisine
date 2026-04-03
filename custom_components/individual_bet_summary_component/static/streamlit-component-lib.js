/**
 * @license
 * Copyright 2018-2021 Streamlit Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

window.Streamlit = {
    setComponentReady: function() {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:componentReady",
            apiVersion: 1
        }, "*");
    },
    setFrameHeight: function(height) {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setFrameHeight",
            height: height
        }, "*");
    },
    setComponentValue: function(value) {
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            value: value
        }, "*");
    },
    RENDER_EVENT: "streamlit:render",
    events: {
        addEventListener: function(type, callback) {
            window.addEventListener("message", function(event) {
                if (event.data && event.data.type === type) {
                    // Safely standardize the event detail for Streamlit components
                    event.detail = event.data;
                    callback(event);
                }
            });
        }
    }
};