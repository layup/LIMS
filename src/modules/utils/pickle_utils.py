import pickle

from base_logger import logger


#TODO: delete this

def save_pickle(dictionaryName):
    logger.info(f'Entering save_pickle with parameter: dictionaryName: {repr(dictionaryName)}')
    try:
        with open("data.pickle", "wb") as f:
            pickle.dump(dictionaryName, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
        logger.error(ex)


def load_pickle(filename):
    logger.info(f'Entering load_pickle with parameter: filename: {repr(filename)}')
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        print("Error during unpickling object (Possibly unsupported):", ex)
        logger.error(ex)
