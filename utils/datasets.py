import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.model_selection import train_test_split


class DataLoader():
    """
    Load dataset and preprocess it to train machine learning algorithms.

    Attributes
    ----------
    data: pd.DataFrame
        Raw dataset.
    X: pd.DataFrame
        Raw input data.
    y: pd.Series
        Raw output data.
    X_train: np.ndarray
        Train input data.
    X_test: np.ndarray
        Test input data.
    y_train: np.ndarray
        Train output data.
    y_test: np.ndarray
        Test output data.
    n_examples: int
        Total number of examples.
    n_features: int
        Number of features in the dataset.
    n_classes: int
        Number of classes.
    classes: np.ndarray
        Class identifiers.
    train_size: int
        Number of examples in the training set.
    val_size: int
        Number of examples in the validation set.
    test_size: int
        Number of examples in the test set.
    """

    data_folder = "./datasets/"

    datasets = {
        "11_tumor": f"{data_folder}11_tumor.csv",
        "9_tumor": f"{data_folder}9_tumor.csv",
        "brain_tumor_1": f"{data_folder}brain_tumor_1.csv",
        "brain_tumor_2": f"{data_folder}brain_tumor_2.csv",
        "cbd": f"{data_folder}cbd.csv",
        "dermatology": f"{data_folder}dermatology.csv",
        "divorce": f"{data_folder}divorce.csv",
        "dlbcl": f"{data_folder}dlbcl.csv",
        "gfe": f"{data_folder}gfe.csv",
        "hapt": f"{data_folder}hapt.csv",
        "har": f"{data_folder}har.csv",
        "isolet5": f"{data_folder}isolet5.csv",
        "leukemia_1": f"{data_folder}leukemia_1.csv",
        "leukemia_2": f"{data_folder}leukemia_2.csv",
        "leukemia_3": f"{data_folder}leukemia_3.csv",
        "lungc": f"{data_folder}lungc.csv",
        "madelon_valid": f"{data_folder}madelon_valid.csv",
        "mfd": f"{data_folder}mfd.csv",
        "orh": f"{data_folder}orh.csv",
        "prostate_tumor_1": f"{data_folder}prostate_tumor_1.csv",
        "qsar_toxicity": f"{data_folder}qsar_oral_toxicity.csv",
        "shd": f"{data_folder}shd.csv",
        "uji_indoor": f"{data_folder}uji_indoor_loc.csv",
        "wdbc": f"{data_folder}wdbc.csv"
        }

    def __init__(self, dataset: str, kfolds: int = None, seed: int = None, verbose: bool = True):
        """
        Parameters
        ----------
        dataset: str
            Name of the dataset that will be loaded and processed.
        kfolds: int or None, default None
            Number of folds in the k-fold cross validation.
        seed: int, default None
            It controls the randomness of the data split.
        verbose: bool, default True
            If True, details about data processing will be shown.
        """

        self.dataset = dataset
        self.kfolds = kfolds
        self.seed = seed
        # Initialize logger with info level
        if verbose:
            logging.basicConfig(encoding="utf-8", level=logging.INFO)

    def _check_header(self, file: str):
        """
        Check if a CSV file has a header.

        Parameters
        ----------
        file: str
            Name of the CSV file.

        Returns
        -------
        has_header: bool
            True if file has a header.
        """
        data = pd.read_csv(file, header=None, nrows=1)
        has_header = data.dtypes.nunique() != 1
        return has_header

    def _get_input(self):
        """
        Get the input data X from the dataset. By default, the penultimate column of the dataset
        is the label and the last is the predefined division of train and test set.
        """
        return self.data.iloc[:,:-2].copy()

    def _get_output(self):
        """
        Get the output data y from the dataset. By default, the penultimate column of the dataset
        is the label and the last is the predefined division of train and test set.
        """
        return self.data.iloc[:,-2].copy()

    def load(self):
        """
        Load dataset according to dataset given as a parameter.
        """
        try:
            path = DataLoader.datasets[self.dataset]
        except:
            # Check if the chosen dataset is available
            raise AssertionError(
                f"The '{self.dataset}' dataset is not available. "
                f"The available datasets are {', '.join(DataLoader.datasets.keys())}."
            )
        # Load dataset
        logging.info(f"Dataset: {self.dataset}")
        if self._check_header(path):
            self.data = pd.read_csv(path, header=None)
        else:
            self.data = pd.read_csv(path)

    def preprocess(self, dropna=True):
        """
        Preprocess the dataset for use in models.

        Parameters
        ----------
        dropna: bool, default False
            Remove rows that contains NaN values.
        """
        # Setting a default representation for NaN values 
        self.data.replace(to_replace = "?", value=np.nan, inplace=True)
        # Remove rows with at least one NaN value
        if dropna:
            self.data.dropna(inplace=True)
            self.data.reset_index(drop=True, inplace=True)

        # Split into input and output data
        self.X = self._get_input()
        self.y = self._get_output()

        # Labels as integer values
        self.y = self.y.astype(int)
        # Set number of examples
        self.n_examples = self.X.shape[0]
        # Set number of features
        self.n_features = self.X.shape[1]
        # Set number of classes
        self.n_classes = self.y.nunique()
        # Get class identifiers
        self.classes = sorted(self.y.unique())
        # Compute imbalance ratio
        minority_class = self.y.value_counts().min()
        majority_class = self.y.value_counts().max()
        self.imbalance_ratio = round(majority_class/minority_class, 4)

    def split(self,
              preset: bool = False,
              val_size: float = 0.0,
              test_size: float = 0.3):
        """
        Split dataset into training, validation and test sets.

        Parameters
        ----------
        preset: bool, default False
            In some works, the training and testing sets have already been defined. To use them,
            just set this boolean variable to True.
        val_size: float, default 0.0
            Proportion of the dataset to include in the validation set. It should be between 0 and
            1. It can be an integer too, but it refers to the number of observations in the
            validation set, in this case.
        test_size: float, default 0.3
            Proportion of the dataset to include in the test set. It should be between 0 and 1.
            It can be an integer too, but it refers to the number of observations in the test set,
            in this case.
        """
        if preset:
            logging.info("Using predefined sets...")
            # Get predefined training set
            train_idx, = np.where(self.data.iloc[:, -1] == "train")
            self.X_train = self.X.iloc[train_idx].to_numpy()
            self.y_train = self.y.iloc[train_idx].to_numpy()
            # There is no validation set
            self.X_val, self.y_val = None, None
            # Get predefined test set
            test_idx, = np.where(self.data.iloc[:, -1] == "test")
            self.X_test = self.X.iloc[test_idx].to_numpy()
            self.y_test = self.y.iloc[test_idx].to_numpy()
        else:
            logging.info("Splitting data...")
            # Split data into training and test sets
            if test_size > 0:
                subsets = train_test_split(self.X.to_numpy(),
                                        self.y.to_numpy(),
                                        test_size=test_size,
                                        random_state=self.seed)
                self.X_train, self.X_test, self.y_train, self.y_test = subsets
                # Split training set into training and validation sets
                if val_size > 0:
                    subsets = train_test_split(self.X_train,
                                            self.y_train,
                                            test_size=val_size/(1-test_size),
                                            random_state=self.seed)
                    self.X_train, self.X_val, self.y_train, self.y_val = subsets
                # Use only training and test sets
                else:
                    # There is no validation set
                    self.X_val, self.y_val = None, None
            else:
                # There is no test set
                self.X_test, self.y_test = None, None
                # Split data into training and validation sets
                if val_size > 0:
                    subsets = train_test_split(self.X.to_numpy(),
                                            self.y.to_numpy(),
                                            test_size=val_size,
                                            random_state=self.seed)
                    self.X_train, self.X_val, self.y_train, self.y_val = subsets
                # Do not split the data. It can be a cross-validation with all data
                else:
                    self.X_train = self.X.to_numpy().copy()
                    self.y_train = self.y.to_numpy().copy()
                    # There is no validation set
                    self.X_val, self.y_val = None, None

        # Set subset sizes
        self.train_size = self.X_train.shape[0]
        self.val_size = self.X_val.shape[0] if self.X_val is not None else 0
        self.test_size = self.X_test.shape[0] if self.X_test is not None else 0
        logging.info(f"Training set with {self.train_size} observations.")
        logging.info(f"Validation set with {self.val_size} observations.")
        logging.info(f"Test set with {self.test_size} observations.")

    def normalize(self, inner_fold=False):
        """
        Transform features by scaling each one between 0 and 1. It is essential for distance-based
        methods.

        Parameters
        ----------
        inner_fold: bool, default False
            If True, normalizes each folder generated by the k-fold split.
        """
        if (self.kfolds is not None) and (inner_fold is True):
            logging.info("Normalizing folds...")
            for k in range(self.kfolds):
                scaler = MinMaxScaler()
                scaler.fit(X=self.train_folds[k][0])
                self.train_folds[k][0] = scaler.transform(X=self.train_folds[k][0])
                self.val_folds[k][0] = scaler.transform(X=self.val_folds[k][0])
                del scaler
                if self.test_size > 0:
                    scaler = MinMaxScaler()
                    scaler.fit(X=self.eval_train_folds[k][0])
                    self.eval_train_folds[k][0] = scaler.transform(X=self.eval_train_folds[k][0])
                    self.eval_val_folds[k][0] = scaler.transform(X=self.eval_val_folds[k][0])
                    del scaler
        else:
            logging.info("Normalizing subsets...")
            scaler = MinMaxScaler()
            # Normalization across instances should be done after splitting the data between
            # training and test set to avoid leakage
            scaler.fit(X=self.X_train)
            self.X_train = scaler.transform(X=self.X_train)
            # When normalizing the validation and test sets, one should apply the normalization
            # parameters previously obtained from the training set as-is
            self.X_val = scaler.transform(X=self.X_val) if self.X_val is not None else None
            self.X_test = scaler.transform(X=self.X_test) if self.X_test is not None else None

    def build_k_folds(self, stratified=False):
        """
        Split the training and test data into k-folds, where the folds are made by preserving the
        percentage of samples for each class.

        Parameters
        ----------
        stratified: bool, default False
            If True, the folds are made by preserving the percentage of samples for each class.
        """
        if self.kfolds is not None:
            logging.info(f"Building {self.kfolds}-folds...")
            self.train_folds = list()
            self.val_folds = list()
            if stratified:
                kfold = StratifiedKFold(n_splits=self.kfolds,
                                        shuffle=True,
                                        random_state=self.seed)
            else:
                kfold = KFold(n_splits=self.kfolds,
                              shuffle=True,
                              random_state=self.seed)
            for train_idx, val_idx in kfold.split(self.X_train, self.y_train):
                self.train_folds.append(
                    [self.X_train[train_idx].copy(), 
                    self.y_train[train_idx].copy()]
                )
                self.val_folds.append(
                    [self.X_train[val_idx].copy(),
                    self.y_train[val_idx].copy()]
                )
            if self.test_size > 0:
                self.eval_train_folds = list()
                self.eval_val_folds = list()
                for train_idx, val_idx in kfold.split(self.X_test, self.y_test):
                    self.eval_train_folds.append(
                        [self.X_test[train_idx].copy(),
                         self.y_test[train_idx].copy()]
                    )
                    self.eval_val_folds.append(
                        [self.X_test[val_idx].copy(),
                         self.y_test[val_idx].copy()]
                    )
