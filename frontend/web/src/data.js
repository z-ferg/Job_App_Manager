// Sample data. Replace with calls to your backend / API.

export const STATUSES = ['Applied', 'Interview', 'Offer', 'Rejected'];

export const student = {
  name: '[Student name]',
  firstName: '[First name]',
  initials: 'HK',
  major: '[Major]',
  classYear: '[Year]',
};

export const sampleApplications = [
  { id: 'a1', company: 'Dominion Energy', role: 'Engineering Co-op', location: 'Richmond, VA', status: 'Applied', applied: '2026-10-25', next: 'No update yet' },
  { id: 'a2', company: 'Northrop Grumman', role: 'Systems Engineer I', location: 'Chantilly, VA', status: 'Applied', applied: '2026-10-22', next: 'Follow up Nov 5' },
  { id: 'a3', company: 'Capital One', role: 'Software Engineering Intern', location: 'McLean, VA', status: 'Interview', applied: '2026-10-14', next: 'Final round Nov 3' },
  { id: 'a4', company: 'Booz Allen Hamilton', role: 'Data Science Intern', location: 'Remote', status: 'Interview', applied: '2026-10-09', next: 'Phone screen Oct 31' },
  { id: 'a5', company: 'Deloitte', role: 'Technology Analyst', location: 'Arlington, VA', status: 'Offer', applied: '2026-09-30', next: 'Respond by Nov 12' },
  { id: 'a6', company: 'Carilion Clinic', role: 'IT Analyst Intern', location: 'Roanoke, VA', status: 'Applied', applied: '2026-09-26', next: 'Follow up Oct 30' },
  { id: 'a7', company: 'Volvo Group', role: 'Manufacturing Intern', location: 'Dublin, VA', status: 'Rejected', applied: '2026-09-18', next: 'Closed Oct 20' },
];

// Fair names, dates and venues are placeholders — load the real schedule from VT Career Services.
export const sampleFairs = [
  { id: 'eng', date: '2026-11-05', name: 'Engineering Career Fair', time: '10 AM – 3 PM', where: 'Cassell Coliseum', employers: null, tags: ['Engineering', 'In person'], kind: 'In person' },
  { id: 'virt', date: '2026-11-09', name: 'Virtual Tech & Data Fair', time: '1 PM – 5 PM', where: 'Online via Handshake', employers: null, tags: ['Computing', 'Virtual'], kind: 'Virtual' },
  { id: 'bus', date: '2026-11-12', name: 'Business Career Fair', time: '11 AM – 4 PM', where: 'Squires Student Center', employers: null, tags: ['Business', 'In person'], kind: 'In person' },
  { id: 'gov', date: '2026-11-18', name: 'Government & Nonprofit Expo', time: '12 PM – 3 PM', where: 'Squires Commonwealth Ballroom', employers: null, tags: ['All majors', 'In person'], kind: 'In person' },
  { id: 'intern', date: '2026-12-02', name: 'Winter Internship Mixer', time: '4 PM – 6 PM', where: 'Online via Zoom', employers: null, tags: ['All majors', 'Virtual'], kind: 'Virtual' },
  { id: 'spring', date: '2027-02-10', name: 'Spring Career Connection', time: '10 AM – 4 PM', where: 'Cassell Coliseum', employers: null, tags: ['All majors', 'In person'], kind: 'In person' },
];

export const sampleReminders = [
  { id: 'r1', title: 'Send thank-you note to Capital One', link: 'Capital One · Software Engineering Intern', due: '2026-10-29T17:00', done: false },
  { id: 'r2', title: 'Follow up with Carilion recruiter', link: 'Carilion Clinic · IT Analyst Intern', due: '2026-10-30', done: false },
  { id: 'r3', title: 'Booz Allen phone screen', link: 'Booz Allen Hamilton · Data Science Intern', due: '2026-10-31T10:00', done: false },
  { id: 'r4', title: 'Update résumé with fall projects', link: 'General', due: '2026-11-01', done: true },
  { id: 'r5', title: 'Capital One final round', link: 'Capital One · Software Engineering Intern', due: '2026-11-03T13:00', done: false },
  { id: 'r6', title: 'Print résumés for Engineering fair', link: 'Engineering Career Fair', due: '2026-11-04', done: false },
  { id: 'r7', title: 'Follow up with Northrop Grumman', link: 'Northrop Grumman · Systems Engineer I', due: '2026-11-05', done: false },
  { id: 'r8', title: 'Respond to Deloitte offer', link: 'Deloitte · Technology Analyst', due: '2026-11-12', done: false },
];
