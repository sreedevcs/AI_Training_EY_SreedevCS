import {useAuth} from '../context/AuthContext';
import {useNavigate} from 'react-router-dom';

export default function About(){
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="container">
        <h1>About Page</h1>
        <p>Welcome, {user.email}!</p>
        <p> You can access this page since you are logged in.</p>
        </div>
    );
}