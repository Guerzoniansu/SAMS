let nav = 0;
let clicked = null;
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : [];


const calendar = document.getElementById('calendar');
const newEventModal = document.getElementById('newEventModal');
const deleteEventModal = document.getElementById('deleteEventModal');
const backDrop = document.getElementById('modalBackDrop');
const eventTitleInput = document.getElementById('eventTitleInput');
const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// const tasks_tab = document.querySelector("#eventDisplayer")
// const tasks = document.querySelector('#eventDisplayer #eventList')
// const selectedDay = document.querySelector('#eventDisplayer #header-task .weekday-s')
// const selectedDate = document.querySelector('#eventDisplayer #header-task .date-s')
// const calendar = document.getElementById('calendar');
// const newEventModal = document.getElementById('newEventModal');
// const deleteEventModal = document.getElementById('deleteEventModal');
// const backDrop = document.getElementById('modalBackDrop');
// const eventTitleInput = document.getElementById('eventTitleInput');
// const descriptionNewTask = document.getElementById('descriptionNewTask');
// const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
// const add_btn = document.querySelector('#add-btn')

// add_btn.addEventListener("click", function() {
//     newEventModal.style.display = 'block'
//     backDrop.style.display = 'block';
// })

// function getDateRepresentation(dateString) {
//     const [month, day, year] = dateString.split('/');
//     const date = new Date(`${year}-${month}-${day}`);
//     const monthNames = [
//         "January", "February", "March", "April", "May", "June", 
//         "July", "August", "September", "October", "November", "December"
//     ];

//     // Format the day with leading zero if needed
//     const formattedDay = String(day).padStart(2, '0');

//     const monthName = monthNames[date.getMonth()];
//     return `${formattedDay} ${monthName} ${year}`;
// }

// function getWeekday(dateString) {
//     const [month, day, year] = dateString.split('/');
//     const date = new Date(`${year}-${month}-${day}`);
  
//     // Get the day of the week and format the day
//     const weekdayName = weekdays[date.getDay()];
  
//     // Return the formatted date with the weekday
//     return weekdayName;
//   }


// function displayTasks(date, daySquare) {
//     clicked = date;
//     const eventsForDay = events.filter(e => e.date === clicked);
//     selectedDay.innerHTML = getWeekday(clicked)
//     selectedDate.innerHTML = getDateRepresentation(clicked)

//     const activeElements = document.querySelectorAll('.active');

//     // Iterate through each element and remove the 'active' class
//     activeElements.forEach(element => {
//         element.classList.remove('active');
//     });
//     daySquare.classList.add("active")
//     tasks_tab.style.display = "flex"

//     tasks.innerHTML = ``
//     if (eventsForDay.length > 0) {
//         eventsForDay.forEach(event => {
//             tasks.innerHTML += `
//                 <div>
//                     <div class="head">
//                         <p class="title">${event.title}</p>
//                         <div class="svg">
//                             <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor"><path d="M280-120q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520ZM360-280h80v-360h-80v360Zm160 0h80v-360h-80v360ZM280-720v520-520Z"/></svg>
//                         </div>
//                     </div>
//                     <p class="content-item">${event.description}</p>
//                 </div>
//             `
//         });
//     }
//     else {
//         tasks.innerHTML = `
//             <p>No tasks here</p>
//         `
//     }

// }

function openModal(date) {
    clicked = date;
  
    const eventForDay = events.find(e => e.date === clicked);
  
    if (eventForDay) {
      document.getElementById('eventText').innerText = eventForDay.title;
      deleteEventModal.style.display = 'block';
    } else {
      newEventModal.style.display = 'block';
    }
  
    backDrop.style.display = 'flex';
  }
  
  function load() {
    const dt = new Date();
  
    if (nav !== 0) {
      dt.setMonth(new Date().getMonth() + nav);
    }
  
    const day = dt.getDate();
    const month = dt.getMonth();
    const year = dt.getFullYear();
  
    const firstDayOfMonth = new Date(year, month, 1);
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const dateString = firstDayOfMonth.toLocaleDateString('en-us', {
      weekday: 'long',
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    });
    const paddingDays = weekdays.indexOf(dateString.split(', ')[0]);
  
    document.getElementById('monthDisplay').innerText = 
      `${dt.toLocaleDateString('en-us', { month: 'long' })} ${year}`;
  
    calendar.innerHTML = '';
  
    for(let i = 1; i <= paddingDays + daysInMonth; i++) {
      const daySquare = document.createElement('div');
      daySquare.classList.add('day');
  
      const dayString = `${month + 1}/${i - paddingDays}/${year}`;
  
      if (i > paddingDays) {
        daySquare.innerText = i - paddingDays;
        const eventForDay = events.find(e => e.date === dayString);
  
        if (i - paddingDays === day && nav === 0) {
          daySquare.id = 'currentDay';
        }
  
        if (eventForDay) {
          const eventDiv = document.createElement('div');
          eventDiv.classList.add('event');
          eventDiv.innerText = eventForDay.title;
          daySquare.appendChild(eventDiv);
        }
  
        daySquare.addEventListener('click', () => openModal(dayString));
      } else {
        daySquare.classList.add('padding');
      }
  
      calendar.appendChild(daySquare);    
    }
  }
  
  function closeModal() {
    eventTitleInput.classList.remove('error');
    newEventModal.style.display = 'none';
    deleteEventModal.style.display = 'none';
    backDrop.style.display = 'none';
    eventTitleInput.value = '';
    clicked = null;
    load();
  }
  
  function saveEvent() {
    if (eventTitleInput.value) {
      eventTitleInput.classList.remove('error');
  
      events.push({
        date: clicked,
        title: eventTitleInput.value,
      });
  
      localStorage.setItem('events', JSON.stringify(events));
      closeModal();
    } else {
      eventTitleInput.classList.add('error');
    }
  }
  
  function deleteEvent() {
    events = events.filter(e => e.date !== clicked);
    localStorage.setItem('events', JSON.stringify(events));
    closeModal();
  }
  
  function initButtons() {
    document.getElementById('nextButton').addEventListener('click', () => {
      nav++;
      load();
    });
  
    document.getElementById('backButton').addEventListener('click', () => {
      nav--;
      load();
    });
  
    document.getElementById('saveButton').addEventListener('click', saveEvent);
    document.getElementById('cancelButton').addEventListener('click', closeModal);
    document.getElementById('deleteButton').addEventListener('click', deleteEvent);
    document.getElementById('closeButton').addEventListener('click', closeModal);
  }
  
  initButtons();
  load();







