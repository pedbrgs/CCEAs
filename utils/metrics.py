from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score

class Metrics():
    
    """
    Evaluates machine learning model according to some evaluation metrics.
    """
    
    def __init__(self, task):

        """
        Parameters
        ----------
        task: str
            Defines the type of the classification task (e.g., multiclass,
            binary).
        """

        self.task = task
        
    def evaluate(self, model, data, verbose = True):
        
        """
        Parameters
        ----------
        model: estimator object
            Model that was chosen by the Halving Grid Search, i.e.,
            estimator which gave the best result on the left out data.
        data: Dataset object
            Object containing the dataset and its post-processing subsets.
        verbose: bool, default True
            If true, show evaluation metrics in the test set.

        Attributes
        ----------
        y_pred: np.array
            Output predicted by the machine learning model given as a
            parameter in the test set.
        conf_matrix: np.array
            Square matrix (CxC), where C is the number of classes, 
            containing the number of true positives (tp), number of false
            positives (fp), number of true negatives (tn) and number of false
            negatives (fn).
        precision: float
            Ratio of the correctly identified positive cases to all the
            predicted positive cases, i.e., tp/(tp+fp). 
        recall: float
            Also known as sensitivity, is the ratio of the correctly
            identified positive cases to all the actual positive cases, i.e.,
            tp/(tp+fn).
        f1_score: float
            Harmonic mean of precision and recall, i.e.,
            2.(precision.recall)/(precision+recall).
        accuracy: float
            Ratio of number of correct predictions to the total number of
            input samples, i.e., (tp+tn)/(tp+fp+tn+fn).
        """
        
        # Predicting
        self.y_pred = model.estimator.predict(data.X_test)
        
        # Type of aggregation used in the evaluation metrics in the
        # multiclass classification task
        avg = 'macro' if self.task == 'multiclass' else 'binary'
        
        # Confusion matrix
        self.conf_matrix = confusion_matrix(data.y_test, self.y_pred)
        # Precision
        self.precision = precision_score(data.y_test, self.y_pred, average = avg)
        # Recall
        self.recall = recall_score(data.y_test, self.y_pred, average = avg)
        # F1-score
        self.f1_score = f1_score(data.y_test, self.y_pred, average = avg)
        # Accuracy
        self.accuracy = accuracy_score(data.y_test, self.y_pred)

        # Showing evaluation metrics
        if verbose:
            print(f"Precision: {self.precision}")
            print(f"Recall: {self.recall}")
            print(f"F1-score: {self.f1_score}")
            print(f"Accuracy: {self.accuracy}")