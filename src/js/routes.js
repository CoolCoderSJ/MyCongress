
import HomePage from '../pages/home.f7';
import SearchPage from '../pages/search.f7';
import ResultsPage from '../pages/results.f7';
import PersonPage from '../pages/biopage.f7';
import BillPage from '../pages/bill.f7';
import NotFoundPage from '../pages/404.f7';

var routes = [
  {
    path: '/',
    id: 'tab1',
    name: 'tab1',
    component: HomePage,
  },
  {
    path: '/search/',
    id: 'tab2',
    name: 'tab2',
    component: SearchPage,
  },
  {
    path: '/results/',
    component: ResultsPage,
  },
  {
    path: '/person/:id',
    component: PersonPage,
  },
  {
    path: '/bill/:billType/:billNumber',
    component: BillPage,
  },
  {
    path: '(.*)',
    component: NotFoundPage,
  },
];

export default routes;